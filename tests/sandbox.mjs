import {connect} from './cdp.mjs';
const {cdp,evaluate,waitFor,close}=await connect(Deno.args[0]);
await cdp('Page.navigate',{url:'chrome://sandbox/'});
await waitFor("document.body && document.body.innerText.includes('Seccomp')");
const status=await evaluate('document.body.innerText');
const pass=/Layer 1 Sandbox\s+(?:Namespace|SUID)/.test(status)&&/PID namespaces\s+Yes/.test(status)&&/Network namespaces\s+Yes/.test(status)&&/Seccomp-BPF sandbox\s+Yes/.test(status);
const report={pass,status};
await Deno.writeTextFile('artifacts/v0.2/sandbox-results.json',JSON.stringify(report,null,2)+'\n');
console.log(`${pass?'PASS':'FAIL'} Chromium sandbox enabled`);close();Deno.exit(pass?0:1);
