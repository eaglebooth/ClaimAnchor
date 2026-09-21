import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const required = (name) => { const value=process.env[name]; if(!value) throw new Error(`Missing ${name}`); return value; };
const account = (name) => createAccount(`0x${required(name).replace(/^0x/,"")}`);
const contract=required("CONTRACT_ADDRESS"), publisher=account("PUBLISHER_KEY"), challenger=account("CHALLENGER_KEY");
const publisherClient=createClient({chain:studionet,account:publisher}), challengerClient=createClient({chain:studionet,account:challenger});
const run=process.env.RUN_ID||Date.now().toString(36);
const sourceUrl="https://raw.githubusercontent.com/eaglebooth/PatchProof/086c4ee10aca8fb208fcb0f7455239ee3f17efb3/docs/LIVE_STUDIONET_EVIDENCE.md";
const counterUrl="https://raw.githubusercontent.com/eaglebooth/ForkRight/011fd33fbe6aa1fde66c8489c6ca3c7b282d6e36/docs/patchproof-independent-verification.md";
const report={contract,network:"studionet-61999",actors:{publisher:publisher.address,challenger:challenger.address},run,sources:{},transactions:[],assertions:[],final:{}};
mkdirSync("docs",{recursive:true});
const save=()=>writeFileSync("docs/live-e2e-run.json",`${JSON.stringify(report,null,2)}\n`);
const source=async(url)=>{const response=await fetch(url);if(!response.ok)throw new Error(`Fetch ${response.status}: ${url}`);const bytes=new Uint8Array(await response.arrayBuffer());return{url,bytes:bytes.length,sha256:createHash("sha256").update(bytes).digest("hex")};};
report.sources.publisher=await source(sourceUrl); report.sources.counter=await source(counterUrl);
const read=async(method,args=[])=>JSON.parse(await publisherClient.readContract({address:contract,functionName:method,args}));
const check=(condition,label,details={})=>{report.assertions.push({label,pass:Boolean(condition),details});save();if(!condition)throw new Error(`Assertion failed: ${label} ${JSON.stringify(details)}`);};
const executionOf=(tx)=>{const values=(tx.consensus_data?.validators||[]).filter(v=>v.vote==="agree").map(v=>v.execution_result);return values.includes("SUCCESS")?"SUCCESS":values.includes("ERROR")?"ERROR":"UNKNOWN";};
const write=async(label,client,method,args,expected="SUCCESS")=>{let hash;try{hash=await client.writeContract({address:contract,functionName:method,args,value:0n});}catch(error){if(expected!=="ROLLBACK")throw error;report.transactions.push({label,hash:null,expected,status:"PRECHECK_REJECTED",execution:"ERROR",error:error instanceof Error?error.message:String(error)});check(true,`${label} rejected before signing`);return null;}process.stdout.write(`${label}: ${hash}\n`);let tx={};for(let i=0;i<300;i++){tx=await client.getTransaction({hash});if(["FINALIZED","CANCELED","UNDETERMINED"].includes(tx.statusName))break;await new Promise(r=>setTimeout(r,2500));}const execution=executionOf(tx);report.transactions.push({label,hash,expected,status:tx.statusName||"UNKNOWN",execution});save();check(expected==="SUCCESS"?execution==="SUCCESS":execution==="ERROR",`${label} ${expected==="SUCCESS"?"succeeded":"reverted"} in GenVM`,{execution,status:tx.statusName});return hash;};

const version=await read("get_contract_version"); check(version.name==="ClaimAnchor"&&version.version===1,"deployed ClaimAnchor V1",version);
const pub=report.sources.publisher,counter=report.sources.counter;
const supportedId=`supported-${run}`, misleadingId=`misleading-${run}`;
const supportedStatement="In the explicitly synthetic PP-2026-001 exercise, PatchProof recorded fixed version 2.4.1 and the separate verification report supported the same root-cause remediation.";
const misleadingStatement="PatchProof proved that a real production parser vulnerability was exploited globally and caused confirmed customer losses before version 2.4.1.";
const grounds="Check whether the statement preserves the synthetic scope and matches the independently documented remediation evidence.";

await write("publish supported citation claim",publisherClient,"publish_claim",[supportedId,supportedStatement,"eaglebooth/patchproof",pub.url,pub.sha256,BigInt(pub.bytes),`pub-supported-${run}`]);
await write("reject duplicate claim",publisherClient,"publish_claim",[supportedId,supportedStatement,"eaglebooth/patchproof",pub.url,pub.sha256,BigInt(pub.bytes),`pub-duplicate-${run}`],"ROLLBACK");
await write("reject self challenge",publisherClient,"challenge_claim",[publisher.address,supportedId,grounds,"eaglebooth/forkright",counter.url,counter.sha256,BigInt(counter.bytes),`self-${run}`],"ROLLBACK");
await write("submit repository-separated challenge",challengerClient,"challenge_claim",[publisher.address,supportedId,grounds,"eaglebooth/forkright",counter.url,counter.sha256,BigInt(counter.bytes),`challenge-supported-${run}`]);
await write("resolve supported claim",publisherClient,"resolve_claim",[publisher.address,supportedId]);
let supported=await read("get_claim",[publisher.address,supportedId]); check(supported.status==="RESOLVED"&&supported.ruling==="SUPPORTED","consensus upheld bounded synthetic claim",supported);
await write("reject double resolution",challengerClient,"resolve_claim",[publisher.address,supportedId],"ROLLBACK");
await write("reject challenge after final ruling",challengerClient,"challenge_claim",[publisher.address,supportedId,grounds,"eaglebooth/forkright",counter.url,counter.sha256,BigInt(counter.bytes),`late-${run}`],"ROLLBACK");

await write("publish misleading citation claim",publisherClient,"publish_claim",[misleadingId,misleadingStatement,"eaglebooth/patchproof",pub.url,pub.sha256,BigInt(pub.bytes),`pub-misleading-${run}`]);
await write("challenge misleading claim",challengerClient,"challenge_claim",[publisher.address,misleadingId,"The source labels the exercise synthetic and provides no evidence of global exploitation or customer losses.","eaglebooth/forkright",counter.url,counter.sha256,BigInt(counter.bytes),`challenge-misleading-${run}`]);
await write("resolve misleading claim",publisherClient,"resolve_claim",[publisher.address,misleadingId]);
const misleading=await read("get_claim",[publisher.address,misleadingId]); check(["MISREPRESENTED","CONTEXT_MISSING"].includes(misleading.ruling)&&misleading.status==="RESOLVED","consensus rejected misleading production claim",misleading);
const publisherRep=await read("get_reputation",[publisher.address]),challengerRep=await read("get_reputation",[challenger.address]);
check(publisherRep.published===2&&publisherRep.supported===1&&publisherRep.faults===1,"publisher telemetry reflects both outcomes",publisherRep);
check(challengerRep.challenges===2&&challengerRep.challenge_wins===1&&challengerRep.challenge_losses===1,"challenger telemetry reflects win and loss",challengerRep);
report.final={supported,misleading,publisherReputation:publisherRep,challengerReputation:challengerRep,stats:await read("get_stats")};save();process.stdout.write(`${JSON.stringify(report,null,2)}\n`);
