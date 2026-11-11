// Original JS state/lifecycle case. Node execution does not validate a browser UI.
import fs from 'node:fs';
const events = new EventTarget();
let value = 0, observed = -1;
const changed = () => { observed = value; };
events.addEventListener('change', changed);
for (let i = 0; i < 20; i++) { value = Math.min(5, value + 1); events.dispatchEvent(new Event('change')); }
const saturated = value === 5 && observed === 5;
value = 0; events.dispatchEvent(new Event('change'));
const reset = value === 0 && observed === 0;
events.removeEventListener('change', changed);
value = 1; events.dispatchEvent(new Event('change'));
const checks = [{name:'state event and unsubscribe',passed:saturated && observed === 0},{name:'bounded reset',passed:reset}];
const passed = checks.every(c => c.passed);
fs.writeFileSync(process.env.GDW_TEST_REPORT, JSON.stringify({engine:'web',engine_version:process.versions.node,passed,checks},null,2),{flag:'wx'});
process.exitCode = passed ? 0 : 1;
