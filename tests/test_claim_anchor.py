import hashlib, json, pytest

def addr(x): return "0x"+bytes(x).hex()
def sha(x): return hashlib.sha256(x.encode()).hexdigest()
COMMIT="1"*40
SOURCE="# Quarterly report\nThe measured uptime was 99.91% for the quarter. Two regional incidents were excluded from the contractual SLA calculation."
COUNTER="# Independent analysis\nRaw availability was 98.7% when the two excluded regional incidents are included. The published 99.91% figure is the contractual SLA metric, not total user-observed uptime."
STATEMENT="The service delivered 99.91% user-observed uptime across all regions during the quarter."
SURL=f"https://raw.githubusercontent.com/publisher/report/{COMMIT}/report.md"
CURL=f"https://raw.githubusercontent.com/auditor/analysis/{COMMIT}/analysis.md"

def published(contract):
    return contract.publish_claim("uptime-q3",STATEMENT,"publisher/report",SURL,sha(SOURCE),len(SOURCE.encode()),"pub-001")

def challenged(contract,vm,publisher,challenger):
    published(contract)
    with vm.prank(challenger):
        return contract.challenge_claim(addr(publisher),"uptime-q3","The claim conflates a contractual metric with total observed availability.","auditor/analysis",CURL,sha(COUNTER),len(COUNTER.encode()),"challenge-001")

def mocks(vm,ruling):
    vm.mock_web(r"report.md",{"method":"GET","status":200,"body":SOURCE})
    vm.mock_web(r"analysis.md",{"method":"GET","status":200,"body":COUNTER})
    vm.mock_llm(r"Determine whether a published statement",json.dumps({"ruling":ruling}))

def test_schema(direct_deploy):
    c=direct_deploy("contracts/claim_anchor.py")
    assert json.loads(c.get_contract_version())=={"name":"ClaimAnchor","schema":"optimistic-citation-challenge-v1","version":1}

def test_publish_validation_is_distinct(direct_deploy,direct_vm):
    c=direct_deploy("contracts/claim_anchor.py")
    with direct_vm.expect_revert("INVALID_STATEMENT"):
        c.publish_claim("uptime-q3","short","publisher/report",SURL,sha(SOURCE),len(SOURCE.encode()),"pub-001")
    with direct_vm.expect_revert("INVALID_SOURCE_URL"):
        c.publish_claim("uptime-q3",STATEMENT,"publisher/report",CURL,sha(SOURCE),len(SOURCE.encode()),"pub-001")

def test_claims_are_publisher_namespaced(direct_deploy,direct_vm,direct_alice):
    c=direct_deploy("contracts/claim_anchor.py"); published(c)
    with direct_vm.prank(direct_alice): published(c)
    assert json.loads(c.get_claim(addr(direct_vm._sender),"uptime-q3"))["exists"]
    assert json.loads(c.get_claim(addr(direct_alice),"uptime-q3"))["exists"]

def test_self_and_same_repository_challenges_rejected(direct_deploy,direct_vm,direct_owner,direct_alice):
    c=direct_deploy("contracts/claim_anchor.py"); published(c)
    with direct_vm.expect_revert("PUBLISHER_CANNOT_CHALLENGE_SELF"):
        c.challenge_claim(addr(direct_owner),"uptime-q3","The statement changes the metric and omits material exclusions.","auditor/analysis",CURL,sha(COUNTER),len(COUNTER.encode()),"challenge-001")
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("COUNTER_SOURCE_NOT_INDEPENDENT"):
        c.challenge_claim(addr(direct_owner),"uptime-q3","The statement changes the metric and omits material exclusions.","publisher/report",SURL,sha(SOURCE),len(SOURCE.encode()),"challenge-001")

@pytest.mark.parametrize("ruling",["SUPPORTED","MISREPRESENTED","CONTEXT_MISSING","CONFLICTED"])
def test_resolution_updates_bounded_state(direct_deploy,direct_vm,direct_owner,direct_alice,ruling):
    c=direct_deploy("contracts/claim_anchor.py"); challenged(c,direct_vm,direct_owner,direct_alice); mocks(direct_vm,ruling)
    assert c.resolve_claim(addr(direct_owner),"uptime-q3")==ruling
    claim=json.loads(c.get_claim(addr(direct_owner),"uptime-q3")); assert claim["status"]=="RESOLVED" and len(claim["ruling_digest"])==64
    publisher=json.loads(c.get_reputation(addr(direct_owner))); challenger=json.loads(c.get_reputation(addr(direct_alice)))
    if ruling=="SUPPORTED": assert publisher["supported"]==1 and challenger["challenge_losses"]==1
    if ruling in ("MISREPRESENTED","CONTEXT_MISSING"): assert publisher["faults"]==1 and challenger["challenge_wins"]==1

def test_unavailable_is_retryable(direct_deploy,direct_vm,direct_owner,direct_alice):
    c=direct_deploy("contracts/claim_anchor.py"); challenged(c,direct_vm,direct_owner,direct_alice)
    direct_vm.mock_web(r"report.md",{"method":"GET","status":503,"body":"down"}); direct_vm.mock_web(r"analysis.md",{"method":"GET","status":200,"body":COUNTER})
    assert c.resolve_claim(addr(direct_owner),"uptime-q3")=="UNAVAILABLE"
    state=json.loads(c.get_claim(addr(direct_owner),"uptime-q3"))
    assert state["status"]=="PUBLISHED" and state["challenger"]==""
    assert json.loads(c.get_reputation(addr(direct_alice)))["challenges"]==0

def test_nonce_replay_blocked_after_unavailable_reopens_claim(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/claim_anchor.py"); challenged(c,direct_vm,direct_owner,direct_alice)
    direct_vm.mock_web(r"report.md",{"method":"GET","status":503,"body":"down"}); direct_vm.mock_web(r"analysis.md",{"method":"GET","status":200,"body":COUNTER})
    assert c.resolve_claim(addr(direct_owner),"uptime-q3")=="UNAVAILABLE"
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("CHALLENGE_NONCE_REPLAY"):
        c.challenge_claim(addr(direct_owner),"uptime-q3","The claim conflates a contractual metric with total observed availability.","auditor/analysis",CURL,sha(COUNTER),len(COUNTER.encode()),"challenge-001")
    with direct_vm.prank(direct_bob):
        c.challenge_claim(addr(direct_owner),"uptime-q3","A fresh challenger can replace unavailable evidence without publisher intervention.","auditor/analysis",CURL,sha(COUNTER),len(COUNTER.encode()),"challenge-002")

def test_malformed_model_output_reopens_claim(direct_deploy,direct_vm,direct_owner,direct_alice):
    c=direct_deploy("contracts/claim_anchor.py"); challenged(c,direct_vm,direct_owner,direct_alice)
    direct_vm.mock_web(r"report.md",{"method":"GET","status":200,"body":SOURCE}); direct_vm.mock_web(r"analysis.md",{"method":"GET","status":200,"body":COUNTER})
    direct_vm.mock_llm(r"Determine whether a published statement",'{"ruling":"SUPPORTED","extra":"invalid"}')
    assert c.resolve_claim(addr(direct_owner),"uptime-q3")=="UNAVAILABLE"
    assert json.loads(c.get_claim(addr(direct_owner),"uptime-q3"))["status"]=="PUBLISHED"

def test_resolved_claim_cannot_be_challenged_again(direct_deploy,direct_vm,direct_owner,direct_alice,direct_bob):
    c=direct_deploy("contracts/claim_anchor.py"); challenged(c,direct_vm,direct_owner,direct_alice); mocks(direct_vm,"MISREPRESENTED"); c.resolve_claim(addr(direct_owner),"uptime-q3")
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("CLAIM_NOT_CHALLENGEABLE"):
        c.challenge_claim(addr(direct_owner),"uptime-q3","A second challenge must not replace a finalized ruling.","other/audit",f"https://raw.githubusercontent.com/other/audit/{COMMIT}/audit.md",sha(COUNTER),len(COUNTER.encode()),"challenge-002")
    with direct_vm.expect_revert("ACTIVE_CHALLENGE_REQUIRED"):
        c.resolve_claim(addr(direct_owner),"uptime-q3")
