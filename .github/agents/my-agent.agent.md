================================================================================

REA (REVERSE ENGINEER ANYTHING) — COMPLETE SINGLE-FILE AGENT INSTRUCTIONS

100% Verbatim Consolidation of All Agent & Skill Files from rea-main

================================================================================



PART 1: CORE REA AGENT SKILL (reverse-engineer-anything + all 6 reference guides)

Use Part 1 (or the entire file) as your GitHub Agent / Copilot system prompt.

All relative reference files (references/*.md) are included verbatim below.

================================================================================





================================================================================

FILE: .agents/skills/reverse-engineer-anything/SKILL.md (Reference path: SKILL.md)

================================================================================



---

name: reverse-engineer-anything

description: Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA. Use shipped-artifact or requested runtime evidence to explain features, compare versions, decompile code, or guide a reconstruction. Skip REA for ordinary source-repository architecture analysis.

metadata:

  version: "44"

---



# REA



Use REA when a claim depends on a shipped binary or package, decompilation,

passive application runtime evidence, or comparison with

behavior not established by available source. For ordinary analysis of a

complete source repository, use normal repository tools and do not run REA

readiness or provider commands.



## Connect only when needed



Installing this skill supplies instructions; it does not register the REA MCP

server, install analysis engines, or add tools to an already-running agent.



If REA tools are available and their registration is not known to be stale,

proceed directly to the target. Do not run diagnostics or setup before every

investigation. Use the connected server's actual tool list and input schemas;

a skill installed from repository main may describe capabilities absent from

an older npm release. Keep complete inline Evidence when that server does not

advertise retained references.



If tools are absent, a call is blocked by the client, or a required provider is

unavailable, read [connection and recovery](https://www.google.com/search?q=references/connection-and-recovery.md).

Diagnose the observed blocker, continue useful supported work, and resume the

original task after repair. Client approval, shell PATH, registration and engine

availability have different remedies; avoid repeating setup for all of them.

If the host times out without a REA result, do not repeat the unchanged call or

assume work stopped. Read the recovery guide's deadline distinction before retrying.



1. Diagnose without changing REA or client configuration. `npx` may download

   the package and write to npm's cache. For Codex, run

   `npx -y rea-agents@latest doctor --client codex --json`. Substitute the current

   supported client: `claude_code`, `claude_desktop`, `codex`, `cursor`,

   `gemini_cli`, `windsurf`, `devin`, `opencode`, `antigravity`, `copilot_cli`,

   `commandcode`, `vscode`, `grok_build`, `omp`, or `grok_bot`. `grok_bot` has no local

   file registration: doctor reports the Grok Bot chat step, and setup does not

   write `mcp.json`. If the client is unknown, use `doctor --json` and

   inspect its registration results before choosing a setup scope.

2. Distinguish the reason. Missing, malformed, or stale registration needs a

   scoped configuration repair. An aligned registration with no tools in the

   active session needs a restart/reconnection; doctor cannot prove that the

   current agent has connected. A missing provider affects only tasks requiring

   that provider: static JavaScript inspection needs neither Hopper nor Ghidra,

   and Android inspection has separate bring-your-own JADX/Java prerequisites.

3. For a configuration repair, prepare the read-only plan:

   `npx -y rea-agents@latest setup --client codex --dry-run --json`.

   Use the current client's ID, show its exact proposed paths, backups, and

   changes, and obtain approval before setup writes configuration or installs

   Hopper. Setup normally installs the matching bundled skill too; include that

   replacement in the reviewed plan. After approval, apply the same scope with

   `npx -y rea-agents@latest setup --client codex --yes`. Add `--install-hopper`

   only if that separate installation was needed and explicitly approved.

4. Restart/reconnect the affected agent. Verify that REA tools actually appear

   in the session, then resume the original investigation. If they remain

   absent, inspect the client's MCP launch error rather than repeating setup.



REA setup never installs or upgrades Node.js, npm, Homebrew, Java, Ghidra, IDA,

JADX, Kuna, Binwalk, or Unblob. Use existing prerequisites; do not install unrelated

software to repair

MCP registration. For an unsupported client, use manual stdio registration

with a version-pinned `rea-agents` package or continue through the CLI.



A concrete CLI fallback for an operator-supplied JavaScript tree or ASAR is:



```bash

npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json

```



No MCP registration or native engine is required. Read the returned Evidence,

graph, limitations, and unknowns with the same care as an MCP result; the CLI

returns the Evidence record directly. This fallback does not establish that

MCP is configured. Native CLI tasks still require their selected engine.

Prefer an existing `rea` CLI. When none is installed and REA package acquisition

is within the authorized scope, use `npx -y rea-agents@latest` in its place.

Configuration repair starts with a read-only setup plan; show paths, backups and

skill replacement before applying authorized changes. Preserve existing approval

and target-execution boundaries. REA setup never installs or upgrades unrelated

software, including Node.js, npm, Homebrew, Java, Ghidra, IDA, JADX, Kuna, Binwalk or Unblob.



## Route the target first



Choose the first tool from the target the user supplied. Use `open_binary` for

active-target native or archive workflows; target-free tools take their own

explicit path or endpoint and do not need it.



- ASAR or extracted JavaScript/Electron tree:

  `analyze_javascript_application`.

- Archive/package member inventory (ZIP/APK/IPA/MSIX/AppX, DMG, or a PyInstaller

  executable): `open_binary` with the supplied local path; use `inspect_artifact`

  when its graph and findings help answer the question. A PyInstaller CArchive

  is the application layer; the bootloader is only the native prefix. Start with

  `detail: "summary"` for large inventories, then use retained inventory views

  for selected member fields/pages. A complete small inventory can cost less

  than extra calls and schemas. Runtime options are metadata, not files.

  Compact delivery still inventories and hashes members. See the

  [Python packaged applications guide](https://www.google.com/search?q=https://github.com/morluto/rea/blob/main/docs/python-packaged-applications.md).

- Apple app plist, Interface Builder, asset catalog, or keyed archive resources:

  `open_bundle_resources`, then the selected resource tool. This does not

  require `CFBundleExecutable` or a deep provider. Resource sessions have no

  executable digest or binary snapshot; use `open_binary` for native code.

- Android APK code, classes, methods, or incoming references:

  `inspect_android_package`, then focused Android tools when advertised.

  Archive member inventory still uses the archive route above.

- Managed PE/CLI assembly: `inspect_managed_artifact`.

- Firmware image: `inspect_firmware_regions` when advertised. Use

  `extract_firmware` when extraction is requested, with a caller-selected new

  absolute output directory. These tools use caller-supplied Binwalk/Unblob on

  Linux; see the [firmware guide](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md).

- .NET NativeAOT PE/ELF: native Ghidra analysis. Native code can yield pseudocode;

  consult the NativeAOT workflow in `references/native-and-artifacts.md` for

  optional metadata recovery and its supported host/layout boundary.

- User-owned browser page already open: `list_browser_targets`.

- Browser action the agent must perform (click, type, navigate):

  `capture_browser_scenario` with declared actions. See

  [runtime observation](https://www.google.com/search?q=references/runtime-observation.md) for connect/launch

  and the focused follow-up browser tools.

- Fiddler Everywhere traffic or a native `.saz` capture: read the

  [Fiddler workflow](https://www.google.com/search?q=references/runtime-observation.md%23fiddler-everywhere-traffic-debugging).

  Inspect saved SAZ with `inspect_web_network_capture` and `format: "saz"`;

  connect Everywhere's separate MCP server for live traffic.

- Retained HAR/SAZ/native mitmproxy/aioquic qlog capture: `inspect_web_network_capture`. Select

  original record ordinals when useful; inspect producer fields and byte/number

  sidecars without fetching recorded URLs or claiming live attribution. See

  [historical captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) for the exact upstream

  profile and credential exclusions. Qlog support starts with aioquic 1.5.0

  JSON 0.3; stream coverage and endpoint loss declarations do not recover bodies

  or establish network loss. Prefer detail summary, then kind qlog trace/stream

  pages; select one trace, stream ID and direction for contribution/range pages.

  Facts retain all-recorded-events-before-selection scope. Other qlog layouts

  and PCAP correlation are unsupported.

- User-owned Electron runtime already open: `list_electron_targets`. Before an electron-main Inspector attempt, check packaged fuses with `inspect_electron_fuses`; disabled `EnableNodeCliInspectArguments` means the app ignores `--inspect`.

- Packet-field discovery: `inspect_packet_fields` searches installed protocols

  and field names/types before choosing fields for `inspect_packet_capture`.

  Query/page the relevant records; registrations do not establish observed traffic.

- Recorded packet captures: `inspect_packet_capture` with selected TShark fields,

  display filters and decode-as rules. Requires Linux, util-linux prlimit and `REA_TSHARK_COMMAND`; see

  [capture guide](https://github.com/morluto/rea/blob/main/docs/packet-captures.md).

  Packet limits count input packets before filtering. Output defaults to 50 matching

  frames; use `match_offset` / `match_limit` for later pages, or explicit null

  limit for complete matching output. Preserve the source digest across pages.

  This does not perform live capture.

  For address/DNS/SNI/protocol summaries use `inspect_pcap_capture` with MCP

  detail summary, then retained kind pcap pages. Requires Wireshark 4.x tshark

  and capinfos, with Linux prlimit or Windows Job Objects; see

  [packet summaries](https://github.com/morluto/rea/blob/main/docs/pcap-analysis.md).

  Select an exact DNS question for address pages; page exhaustion does not prove

  network completeness. This reads recordings and does not acquire traffic.

- Decoder discovery: `inspect_signal_decoders` searches installed decoder IDs

  or selected decoder help, including channels and options. Query and page the

  relevant details before choosing settings; this does not scan hardware.

- Recorded logic/signal traces: `decode_signal_recording` with explicit decoder,

  channel and protocol settings. On Linux with util-linux prlimit, supply sigrok-cli 0.7.2 through

  `REA_SIGROK_COMMAND`; see [recording guide](https://www.google.com/search?q=https://github.com/morluto/rea/blob/main/docs/signal-recordings.md).

  Output defaults to 50 literal lines; select annotation classes and page with

  `line_offset` / `line_limit`, or explicit null for all remaining output.

  Window counts are display lines, not annotations or samples. Preserve source digests across pages.

  This reads existing files; it does not acquire hardware signals.

- Explicit local WebAssembly artifact: `inspect_wasm_artifact`. Supply WABT 1.0.42

  through `REA_WABT_BIN_DIRECTORY`; retain exact byte/tool identity and decoded WAT.

  Select JavaScript glue and candidate paths explicitly and preserve URL/path

  ambiguity. No implicit fetch or target execution; WAT is not original source.

  See the [WASM guide](https://www.google.com/search?q=https://github.com/morluto/rea/blob/main/docs/wasm-artifacts.md).

- Explicit local EVM bytecode carrier: `inspect_evm_interface` with caller-selected

  `raw` or `hex` encoding. Preserve carrier/decoded digests and treat selectors,

  argument strings and mutability as inferred candidates; this performs no chain

  lookup or target execution. For the complete inferred interface without hex or

  duplicate stdout, discover support and select `detail: "summary"`; complete

  Evidence stays retained under its original identity. Use the returned

  `parent_evidence_id` for exact function or `bytecode_hex`/stdout/stderr pages.

  Candidate coverage does not establish interface completeness. See the

  [EVM bytecode guide](https://github.com/morluto/rea/blob/main/docs/evm-bytecode.md).

- Embedded Go compiler, module or build-setting metadata: `inspect_go_binary`

  with the explicit local file. This built-in target-free inspection requires no

  Go installation or disassembler. Preserve raw module bytes and source ranges;

  absent metadata does not prove a binary is not Go, and unparsed text records

  remain explicit. See the

  [Go binary guide](https://github.com/morluto/rea/blob/main/docs/go-binaries.md).

- Bundled GGUF or safetensors model declarations: `inspect_model_artifact`

  with the explicit local file. Default header hashing leaves full-file identity

  unknown; `hash: "full"` additionally reads all weights for SHA-256. MCP returns

  retained summaries; optional `view` selects one page in the initial call. Use

  `inspect_analysis_view` kind `model-artifact` for

  batched metadata keys, tensor names or type totals, selected fields and pages.

  Preserve header-scoped indices and array preview omissions; do not infer model

  behavior from declared architecture or tensor types. See the

  [model file guide](https://github.com/morluto/rea/blob/main/docs/model-artifacts.md).

- Unity IL2CPP names, member owners and string literals from `global-metadata.dat`:

  `inspect_il2cpp_metadata` with the explicit local file; MCP defaults to compact

  counts. Query sections, images, types, methods, fields, properties, events,

  parameters or string_literals through `inspect_analysis_view`

  with the returned `parent_evidence_id`, using exact filters, batch indices and

  selected fields. Parameters accept `method_indices`, avoiding a scan of all

  parameter pages. Missing collections in historical Evidence remain unknown.

  Versions 24, 27, 29, 31 and 39; no Unity, IL2CPP

  binary or disassembler is run. Unrecognized magic (possibly encrypted) and

  other versions are unsupported. Optional matching `binary_path` enables static native addresses and type references; query `method_addresses` with indices or addresses/states, preserving every shared-body method and both artifact identities. Without a linked binary native counts remain unknown. Byte-pattern fallback is inferred; no runtime behavior or same-build pairing is proved. See the

  [IL2CPP metadata guide](https://github.com/morluto/rea/blob/main/docs/il2cpp-metadata.md).

- Embedded cargo-auditable Rust dependency metadata: `inspect_rust_binary`

  with the explicit local ELF, PE, or thin Mach-O file. This built-in

  target-free inspection requires no Rust installation or disassembler. Preserve

  package order, dependency indices, and the section file range. A missing

  `.dep-v0` section is null metadata, not proof the binary has no dependencies.

  A rustc commit hash is an inference from a read-only `/rustc/<40-hex>/` path.

  See the

  [Rust binary guide](https://github.com/morluto/rea/blob/main/docs/rust-binaries.md).



- Explicit local SQLite database snapshot: `inspect_sqlite_database`. Inspect

  with Node.js 24.x >=24.15 or 26+ providing native SQLite limits. Read schema

  first (compact inventory by default), or select an exact ordinary table

  and `columns` when rows are needed. Defaults are selected-table schema and

  20 rows; request `schema_scope: "database"` for the complete stored schema. Preserve both database and existing sibling WAL identity; row samples

  report truncation and have unspecified order. Use a quiescent snapshot rather

  than assuming a live database/WAL pair was copied atomically. See the

  [SQLite guide](https://github.com/morluto/rea/blob/main/docs/sqlite-databases.md).

- Explicit Linux ELF file for offline layout, symbols, relocations or static

  mitigation evidence: `inspect_binary_layout`. This target-free operation uses

  caller-supplied pwntools without opening a disassembler database. Preserve its

  raw locations and inference/coverage limits; see the

  [offline binary guide](https://github.com/morluto/rea/blob/main/docs/binary-diagnostics.md).

- Supplied Linux x86-64 ELF core: `inspect_recorded_crash`. Read every recorded

  thread, raw note and source-bound register without opening a live target.

  Historical PIDs do not select live processes. Request `include_debugger_context`

  only when core-only mapping candidates help; see the

  [recorded crash guide](https://github.com/morluto/rea/blob/main/docs/recorded-crashes.md).

- PE resource type/name/language trees and static icon group references:

  `inspect_pe_resources` with an explicit path. This portable operation requires

  no active target or engine; opaque payloads retain file ranges and SHA-256.

- Native executable, library, or analysis database: `open_binary`, then

  use focused analysis tools directly; call `binary_overview` when metadata or

  inventory context is useful and available from the selected provider.



For an existing IDA MCP configuration, use `open_binary` with the original

input binary and `provider_id: "ida"`; do not pass an `.idb` or `.i64` database.

The legacy attached profile binds the already-open GUI input by SHA-256 and

leaves its database open. The modern headless profile creates and closes an

owned private database without saving. Installation and registration reuse

[mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp); see the

[IDA provider guide](https://github.com/morluto/rea/blob/main/docs/ida-provider.md).

Proceed directly to `analyze_function`, pseudocode, or function/string searches

after opening; IDA does not supply `binary_overview`. Consult session availability

when composing broader workflows. Modern direct callers and unsupported dossier

facets remain unknown; live IDA results are not replayed from snapshots.



With `REA_KUNA_COMMAND` configured, `provider_id: "kuna"` answers procedure

lists, lookups, pseudocode, assembly and `analyze_function` from Kuna's cached

whole-program export. Callers/callees use a separate body-free graph shared by

the session; `xrefs` returns exact-address incoming sites and filters forwarding

aliases. These queries and inventory lookups do not trigger a C export. Indirect

targets remain unknown and can make relationship coverage partial. Reference

caches expire on close; a fresh CLI process repeats the native reference walk.

Typed references, CFG, raw-memory tools and annotations remain unsupported. A cold first

answer can come from a single-function run (its limitations say so); assembly

waits for the export. For pseudocode and assembly, `raw_result.source` names the

cached `.c`/`.asm` file and byte span, which you may search directly instead of

calling per function. See the

[Kuna provider guide](https://www.google.com/search?q=https://github.com/morluto/rea/blob/main/docs/kuna-provider.md).



If the user says only "my app" without a name, path, or target already selected

for this task, ask which app before searching for artifacts. Paths in unrelated

saved reports and nearby test fixtures do not select the user's target. Resolve

an actual human-readable app name to one clear installed artifact when possible;

ask when matches are ambiguous. Never choose an example app on the user's behalf.



In a target-free session, use `open_binary` to bind any archive/package or

native target whose analysis tool operates on the active target. Do not call an

unadvertised tool; inspect `binary_session` with `{}` and its

`result.tool_availability` for availability reasons and remediation. Expand each

group's `names` into entries, inheriting the inventory-level client requirements

unless the group overrides them. In its closed effect and annotation vocabularies,

listed flags are true and omitted known flags are false. The grouped name union

is the complete tool inventory; use `tools/list` for canonical tool schemas.

Provider candidate facts describe possible providers, while top-level session

capabilities describe the current route and `analysis_provider_binding` names the

selected provider. Do not treat those scopes as interchangeable.



For a Ghidra startup timeout on a large native target, follow

[deadline recovery](https://www.google.com/search?q=references/native-and-artifacts.md%23ghidra-startup-deadline-recovery)

before abandoning deep analysis or repeating the same cold import. The default

330 seconds is configurable; changing the server's environment requires a new

REA process.



## Work summary-first



Start with the default result and use its inline Evidence and graph context.

For a JavaScript application or ELF layout whose size is unknown or large,

call `analyze_javascript_application` or `inspect_binary_layout` with

`"detail": "summary"`, then inspect the retained `parent_evidence_id` with

`inspect_analysis_view`.

Page module identities and select the returned `node_id` before requesting an

item; a single file path can represent several graph roles. Do not repeat an

identical analysis or rejected call without a changed input or resolved blocker.

Recheck session state when a lifecycle change makes that status useful.

Make a focused follow-up only when the

returned result leaves a specific question unanswered.



If MCP reports `resource_constraint` with `details.resource: "transport"`, call

`inspect_analysis_view` with its reported same-session Evidence reference for a

summary, one section/module, or a stable page. Use `trace_application_feature`

once a seed is known, or call `export_evidence_bundle` to write the complete

session to a selected path. The analysis remains complete in the ledger; avoid

repeating it merely to request the same oversized response. Complete CLI JSON

output also streams without a single MCP frame.



When the retained parent ID is unknown, use `get_evidence_bundle` with

`detail: "summary"` and exact filters for operation, target SHA-256,

analysis-profile digest or canonical procedure address. Select its returned

Evidence ID for the next view instead of requesting the complete bundle.

`retention: "complete-record"` means the whole record is stored; native

value-flow truncation and unknown metadata remain separate. For an exported

portable bundle, use `rea inspect-evidence-bundle` with JSON containing `path`,

`detail: "summary"` and the same `filters`. Reading that file still requires

validating its full contents within the local memory budget.



A client can also truncate a successful tool result without a REA transport

error. Treat that preview as incomplete; use the retained parent ID for smaller

views or export when the full record is needed. Do not parse the preview as

canonical JSON or repeat the producer. For JavaScript, read the

[module-view and trace recipes](https://www.google.com/search?q=references/javascript-applications.md) before

drilling into a large graph; a broad bidirectional trace can expand unrelated

containment relationships even after summary analysis.



Every conclusion must distinguish observations, inferences, and unknowns. Cite

Evidence IDs, preserve limitations and incomplete coverage, and never imply

that static analysis observed execution. Runtime requests execute the declared

target and lifecycle; do not broaden the target or action beyond those fields.



Within the user's requested investigation, call available analysis tools

directly. REA does not require permission grants or per-call approval flags.

The agent client can independently require approval. Follow the declared request

scope and the host's actual access requirements; use the recovery guide for an

observed client-policy rejection.



## Plan broader investigations



For requests that span multiple features or subsystems, use a staged workflow:



1. Turn the request into a checklist of questions and the evidence each answer

   needs. Resolve target identity and constraints from the conversation and

   workspace before asking for information again.

2. Inspect the current REA session, artifact identity, saved analysis database,

   bookmarks, and prior evidence. Reuse matching state; do not open duplicate

   sessions or repeat identical analysis.

3. Start with the smallest useful overview or inventory. Follow each question

   from its entry point through relevant data and state changes to its result.

   Batch related operations around a specific hypothesis, then expand only when

   the returned evidence leaves a concrete gap.

4. Inspect relevant packaged resources and configuration alongside code when

   they affect the question. Use format-aware inventory and parsers; do not

   infer behavior from filenames, strings, or layout alone.

5. Corroborate a conclusion with the evidence type it requires. Use runtime

   observation only when static evidence cannot answer the question and the

   required host runtime and OS access are available. For JavaScript behavior,

   run probes against the actual app through the available browser, Electron,

   or process capture workflow.

6. Decompose work into independent questions. When parallel workers are

   available and the questions do not depend on one another, assign distinct

   scopes, point workers to existing evidence, and ask them to return sources,

   conclusions, and unresolved gaps. Otherwise, work sequentially.

7. Keep a concise finding ledger linking each conclusion to Evidence IDs,

   confidence/evidence type, search boundary, and remaining unknowns. Update

   the shared index or investigation report so later passes can reuse results.



Before finishing, revisit the original checklist. Mark each question as

answered, partially answered, or unresolved based on its evidence; keep

bounded negative searches bounded, and do not describe a broad investigation

as complete while required questions remain open.



## Read only the relevant guide



- Native binaries, managed assemblies, archives, and extraction:

  [references/native-and-artifacts.md](https://www.google.com/search?q=references/native-and-artifacts.md)

- ASARs, extracted JavaScript, feature tracing, and version comparison:

  [references/javascript-applications.md](https://www.google.com/search?q=references/javascript-applications.md)

- Android APK declarations, classes, methods, and static references:

  [references/android-applications.md](https://www.google.com/search?q=references/android-applications.md)

- Browser/Electron observation (passive and scenario) and static/runtime

  reconciliation:

  [references/runtime-observation.md](https://www.google.com/search?q=references/runtime-observation.md)

- Evidence paging, comparisons, residual unknowns, and verification:

  [references/evidence-workflows.md](https://www.google.com/search?q=references/evidence-workflows.md)



## Finish the task



Explain findings in plain language and tie them to returned evidence. When the

user asks to build something, use normal coding tools and separate observed

behavior from design choices. Close an opened native session with

`close_binary` when the investigation is complete.





================================================================================

FILE: .agents/skills/reverse-engineer-anything/https://www.google.com/search?q=references/connection-and-recovery.md (Reference path: https://www.google.com/search?q=references/connection-and-recovery.md)

================================================================================



# Connection and task recovery



Read this guide only for an observed connection, command, approval or provider

blocker. Keep the user's target and question in view. Explain what prevented the

operation and the next useful step; after repair, continue the investigation.



Commands below use an installed `rea`. If none is available, use the package

invocation in `SKILL.md` when acquiring REA is authorized. Follow the connected

server's schemas and the installed CLI's help rather than assuming repository

main and an older release expose the same arguments.



## Choose the remedy from the observed failure



| Observation                                                     | Meaning and next step                                                                                                                                                                                                                                                                                                 |

| --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| No REA tools in the active session                              | Inspect registration with `rea doctor --client codex --json`. A skill installation alone does not register MCP.                                                                                                                                                                                                       |

| Missing, malformed or stale registration                        | Prepare a scoped setup plan; apply only authorized changes with backups.                                                                                                                                                                                                                                              |

| Aligned registration, but no connected tools                    | Restart/reconnect the client. Doctor checks registration; it cannot establish the current agent's connection. Inspect the client's launch error if reconnection fails.                                                                                                                                                |

| `MCP tool call requires approval, but approval policy is never` | Codex rejected the call before REA executed it. Do not install an engine or repeat setup to solve this client-policy decision. See the approval section below.                                                                                                                                                        |

| REA returns `provider_unavailable` or an unavailable tool entry | Read that operation's provider diagnostics or `binary_session.result.tool_availability`. Expand each group's tool names and inherit the shared client requirements unless overridden. Use the operation's availability, reason, and remediation; a complete tool catalog does not imply every operation is available. |

| `rea` is missing in a child shell, or Node is incompatible      | Inspect the actual shell PATH and launcher/runtime. A prefix installation may be absent from a login shell's PATH; this does not establish a broken MCP registration.                                                                                                                                                 |



If the client cannot launch its shell/sandbox helper or read the installed skill,

inspect its launch diagnostic. For example, Codex can refuse helper aliases when

CODEX_HOME is under `/tmp`; use an authorized profile outside the OS temporary

directory. REA setup cannot repair the client's executor. Preserve the sandbox

instead of silently disabling it to make an analysis command work.



Static JavaScript and ordinary ZIP inventory need neither Hopper nor Ghidra.

HAR inspection is offline and does not require a live browser. Native

decompilation, Android analysis and firmware extraction have their own

bring-your-own prerequisites. Use supported inventory/static evidence when it

answers part of the question, and name the unavailable evidence separately.

Do not substitute another target. Label observations from ordinary shell tools

as such; only actual REA output supplies REA Evidence.



## Distinguish client and server deadlines



A host message such as `timed out awaiting tools/call` with no REA result means

the client's deadline expired before a result arrived. It does not establish

that REA finished, canceled successfully, or released all resources. Do not

repeat the unchanged analysis. Inspect available session/provider state and

retained Evidence only when useful; an idle `binary_session` is not proof that

every target-free operation stopped. Never invent a missing Evidence reference.



Allow the host tool deadline to cover execution, cancellation/cleanup, and

response delivery. In Codex, the setting is

`mcp_servers.<server-id>.tool_timeout_sec` in **seconds**, not

`startup_timeout_sec`. Select a value for the actual operation budget and

headroom, not a universal timeout. See the

[official MCP configuration reference](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

Apply configuration changes only within the authorized scope, preserving

unrelated entries and backups; reconnect/restart as required by the host.

When configuration is not editable, report the setting needed or use an

authorized CLI fallback. Do not silently broaden permissions or switch targets.



A returned REA `provider_timeout` instead means the **server/provider** reached

its deadline. Follow its `remediation.action`, reuse accessible partial Evidence,

and resolve reported incomplete cleanup before retrying. Raising only the

client deadline does not change this server budget. For static JavaScript,

`analysis_timeout_ms` (CLI `rea analyze-javascript-application <path>

--analysis-timeout-ms <milliseconds>`) controls each source's

startup, analysis and transfer deadline in **milliseconds**. Increase that

budget or reduce semantic work / select exact inventoried `source_paths` when

the task permits. Omit `source_paths` for all sources; `[]` is invalid.

`detail: "summary"` reduces delivery, not analysis work. A per-source budget

does not bound the elapsed time for an entire multi-source application.

Partial-Evidence inspection can avoid recomputation; an unavailable reader is

not itself a reason to block a corrected static-analysis retry.

The shorthand `rea analyze <path>` does not expose this timeout flag; use the

explicit JavaScript command when changing that budget.



For invalid arguments, use the connected tool's current input schema, or the

installed CLI's command help. Refresh the catalog if stale; do not guess fields

from an older skill or return the entire catalog to repair one field. Correct

all reported fields before retrying.



## Repair registration when needed



For Codex:



```bash

rea doctor --client codex --json

rea setup --client codex --dry-run --json

```



Use the current supported client's ID: `claude_code`, `claude_desktop`, `codex`,

`cursor`, `gemini_cli`, `windsurf`, `devin`, `opencode`, `antigravity`,

`copilot_cli`, `commandcode`, `qwen_code`, `vscode`, `trae`, `grok_build`, `omp`, `pi`,

`hermes`, `qoder`, `droid`, `zcode`, `dsh`, or `grok_bot`. If unknown, inspect `doctor --json` before choosing a

scope. `grok_bot` uses a chat registration step rather than local `mcp.json`.

For unsupported clients, use version-pinned manual stdio registration or CLI.



Show the plan's exact paths, backups, changes and bundled-skill replacement.

Obtain approval for writes when that concrete scope is not already authorized,

then apply the same scope with `rea setup --client codex --yes`. Add

`--install-hopper` only when separately needed and explicitly approved. Do not

install or upgrade unrelated prerequisites. Restart/reconnect, verify tools

actually appear, and resume the original task. If they remain absent, inspect

the launch failure rather than looping through setup.



## Codex tool approval is separate from REA readiness



REA tools have no permission-grant handshake. Codex can still require approval

because an operation creates owned resources, launches a helper or has cleanup

effects. An advertised tool or successful doctor result does not override that

client policy. `workspace-write` alone does not resolve an MCP approval

rejection, and `approval_policy = "never"` does not mean every MCP tool is

preapproved.



When interactive approval is available, use the client's approval flow for the

requested operation. In an unattended run, continue through an authorized CLI

workflow if the execution environment permits it, or report the blocked

operation and the approval needed to proceed. Do not retry the same rejected

call, silently broaden approvals, or rewrite MCP effects as read-only.



For an operator who explicitly wants to preapprove named operations in a

disposable Codex profile, current Codex supports per-tool configuration. For

example, opening and closing an analysis session can be scoped independently:



```toml

[mcp_servers.rea.tools.open_binary]

approval_mode = "approve"



[mcp_servers.rea.tools.close_binary]

approval_mode = "approve"

```



Use the actual server ID and only the operations whose effects were approved;

this example does not approve inspection, extraction or runtime execution.

Show the proposed config edit and preserve unrelated entries and backups before

writing. Managed policy can constrain client settings. Consult the

[Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

for the installed client's supported settings. This is an optional recovery

choice, not a prerequisite for every REA task.



## Continue through an installed CLI



Check the command environment only if the launcher fails:



```bash

command -v rea

command -v node

node --version

rea --version

```



Use the public launcher at its known installation path with a supported existing

Node on PATH when the child shell loses a prefix installation. Avoid internal

`dist/cli.js` entrypoints or global toolchain changes. MCP may have its own valid

launcher even when a shell cannot resolve `rea`.



For a user-supplied JavaScript tree or ASAR, select output files in the authorized

workspace and save complete Evidence before reading a view:



```bash

rea analyze-javascript-application /absolute/path/to/app --json > app-evidence.json

jq -c '{source: {kind: "inline", evidence: .}, view: {kind: "summary"}}' app-evidence.json > app-view.json

rea inspect-analysis-view app-view.json

```



These commands do not register MCP or install an analysis engine. CLI JavaScript

JSON is complete and can be very large; redirect it rather than loading it into

context. Use an existing JSON processor if `jq` is absent, without installing

one just for this recipe. Inspect a module page or item using the same inline

source and the [JavaScript recipes](https://www.google.com/search?q=javascript-applications.md). Preserve graph

coverage, limitations and unknowns. Native CLI analysis still requires its

selected engine, and all CLI operations retain the host's execution permissions.





================================================================================

FILE: .agents/skills/reverse-engineer-anything/https://www.google.com/search?q=references/native-and-artifacts.md (Reference path: https://www.google.com/search?q=references/native-and-artifacts.md)

================================================================================



# Native, managed, and packaged artifacts



For release comparisons, export `list_procedures` Evidence from each target before

closing it. Close clears session records: import both bundles after collecting the

two targets, or supply portable inline Evidence. `match_native_functions` pairs unique exact names and, when supplied,

complete observed body bytes. Reuse optional same-context `list_names`,

`procedure_info`, `read_bytes` and existing `analyze_function` Evidence; avoid

decompiling every function merely to match it. Its summary retains a parent for

`inspect_analysis_view` `function-matches` collections `matches` and `functions`.

Select columns, batch IDs and page individual facts; aliases remain unresolved.

Unpaired observations do not prove additions/removals. Existing matched dossier

pairs include inputs for `compare_functions`; otherwise analyze just chosen pairs.



## Apple app resources



Use `open_bundle_resources` with the selected app path, then `inspect_plist`,

`decode_interface_builder`, `inspect_asset_catalog`, or `inspect_keyed_archive`.

The resource session reads the app without resolving `CFBundleExecutable` or

starting a deep provider. Preserve `resource_root` provenance, per-resource

hashes where reported, and null executable identity; a directory path is not

an executable digest. Export retained Evidence before closing or switching

roots. Binary analysis snapshots do not apply. Use `open_binary` to switch to

executable analysis, and `close_binary` to release either session kind.



The four matching CLI commands accept the app path directly. For an archive

inside the app, use `inspect-keyed-archive APP_PATH RELATIVE_ARCHIVE_PATH`.

Host requirements for plist and compiled asset/Interface Builder tooling still

apply; a resource-only session does not establish provider availability.



## Desktop installation directories



When an installation directory is supplied and its runtime is unknown, use

`inspect_desktop_application` with its absolute path. Default MCP summary

delivery retains complete Evidence. Read `files`, `omissions`, `candidates`, `components` or

`next_probes` with `inspect_analysis_view` kind `desktop-application`, selecting

exact paths, batched file/omission IDs or families and only needed fields and pages.

Summary `probe_issues` retains counts and bounded previews. Select files with

`has_issues: true` and fields `path`, `read_status`, `issues` to retrieve exact

failures directly; preview text is display data, while `file_id` selects full facts. Preserve source

coverage, read-range identity and unknowns; directory snapshot identity is not

a digest of every file's contents. Component path markers do not establish

runtime presence. For compact CLI output, use

`inspect-desktop-application PATH --detail summary --evidence_output BUNDLE`.

See [desktop installations](https://github.com/morluto/rea/blob/main/docs/desktop-applications.md).



## Go build metadata



Use `inspect_go_binary` for an explicit local ELF, PE or thin Mach-O when the

question concerns the embedded compiler version, module/dependency versions,

local replacements or build settings. No `open_binary`, Go installation or

target execution is required. The CLI equivalent is `inspect-go-binary PATH`.

Preserve artifact SHA-256, original file ranges, framed module bytes and every

unparsed module-text line. A missing record is an unknown, not proof of a

non-Go binary; observed metadata does not authenticate its claims. Function,

source and type recovery remain a separate native-analysis question.



## Model files



Use `inspect_model_artifact` (`inspect-model-artifact PATH`) for local GGUF v2/v3

and safetensors declarations without a model runtime. Header-only mode does not

read weights or establish full-file identity. `hash: "full"` explicitly streams

all bytes. Retained `model-artifact` views page `metadata`, `tensors` and derived

`types`, with exact batch filters and selected fields. Arrays retain typed counts

and eight-element previews; omitted values, unknown types and runtime behavior

stay explicit. See [model files](https://github.com/morluto/rea/blob/main/docs/model-artifacts.md).



## IL2CPP metadata



Use `inspect_il2cpp_metadata` for an explicit local Unity `global-metadata.dat`

(versions 24, 27, 29, 31 and 39) when the question concerns assembly images,

names, member owners, string literals, namespaces or index ranges. No `open_binary`, Unity installation or target

execution is required. The CLI equivalent is `inspect-il2cpp-metadata PATH`.

MCP defaults to counts with complete retained Evidence. Query `sections`,

`images`, `types`, `methods`, `fields`, `properties`, `events`, `parameters` or

`string_literals` through `inspect_analysis_view`; use exact names,

batch indices and selected fields. Row indices are scoped by artifact SHA-256

and collection; page offsets count filtered matches. Parameters support batch

`method_indices` to read one method's parameters directly. Historical reports

without member collections retain unknown counts rather than empty inventories. Preserve

artifact SHA-256 and index widths. Unrecognized magic may mean encryption and

is unsupported, not decrypted. Linking names to `GameAssembly` or

`UnityFramework` code addresses remains a separate native-analysis question.

See [IL2CPP metadata](https://github.com/morluto/rea/blob/main/docs/il2cpp-metadata.md).



## Rust dependency metadata



Use `inspect_rust_binary` for an explicit local ELF, PE, or thin Mach-O when

the question concerns the cargo-auditable crate list embedded in `.dep-v0`

(Mach-O: `__DATA,.dep-v0`). No `open_binary`, Rust installation, or target

execution is required. The CLI equivalent is `inspect-rust-binary PATH`.

Preserve artifact SHA-256, package order, dependency indices, and the section

file range. A missing section is null metadata, not proof the binary has no

dependencies. An omitted package kind stays null. A rustc commit hash is

inferred from a read-only `/rustc/<40-hex>/` path and does not by itself

identify the compiler. See [Rust binaries](https://github.com/morluto/rea/blob/main/docs/rust-binaries.md).



## SQLite snapshots



Use `inspect_sqlite_database` with an explicit local database snapshot for its

schema and optional rows from one exact ordinary table. It requires Node.js

24.x >=24.15 or 26+ with the native `DatabaseSync.limits` API. It also consumes the

existing sibling `-wal`; retain both original digests when citing its result.

Default output is a compact inventory; a selected table expands only its own

schema and samples 20 rows. Select `columns` to avoid irrelevant or large cells,

and request `schema_scope: "database"` only for complete schema details.

Choose `row_limit` when a finite sample is useful and keep truncation and

unspecified row order explicit. Virtual tables, shadow tables and views are

schema facts, not row-read targets. REA inspects private copies and leaves

the source files untouched; obtain a coherent quiescent database/WAL snapshot

before inspection. See [SQLite snapshots](https://github.com/morluto/rea/blob/main/docs/sqlite-databases.md).



## Recorded Linux crashes



Use `inspect_recorded_crash` with an explicit Linux x86-64 ELF core path to

inspect historical thread registers, signals, raw notes and original file

ranges. It is independent of the active disassembler target. Source-bound

register values and note bytes are observations; missing notes, signal-thread

association and current executable/library identity remain unknown. PIDs are

historical metadata and never authorize live attach or control.



The optional `include_debugger_context` facet adds mapping candidates through

caller-supplied GDB/pwndbg in an owned core-only session. Display names do not

establish current file identity; zero reported flags leave permissions unknown.

Requested unavailable context fails with setup guidance. See

[recorded crashes](https://github.com/morluto/rea/blob/main/docs/recorded-crashes.md)

for exact upstream profiles, bounds and verification coverage.



## Offline ELF layout



Use `inspect_binary_layout` with an explicit local ELF path for file-backed

sections, symbols, relocations, linkage names, and static mitigation inferences

without opening a disassembler target. When that complete record is already

retained, call `inspect_analysis_view` for a summary, mitigations or linkage

facet, one section or symbol, or a stable page. Do not re-run the decoder to

read a single object.



## Offline WASM



Use `inspect_wasm_artifact` with caller-supplied WABT for selected local bytes.

For counts, validation and WAT identity, select `detail: "summary"` on the first

MCP call. The complete original Evidence stays retained; use

`normalized_result.parent_evidence_id` for exact exports or text pages. Omitted

or complete detail keeps the existing complete result.

For a completed result, use `inspect_analysis_view` with its reported retained

reference for a summary or `view: {kind: "wasm", facet: "exports", offset: 0, limit: 32}`.

Facets also include sections, imports, candidates, glue, WAT, headers, details

and tool profile. Text offsets count UTF-16 code units; follow `next_offset`.

The complete source remains retained after an oversized MCP reply. No target

execution or network acquisition is implied, and WAT is decoded representation.



## Native targets



After `open_binary`, use focused search, procedure, or function tools directly.

Use `binary_overview` when target metadata or inventory context helps answer the

question. Prefer literal search, names, decompilation, callers, callees, and

cross-references. Addresses and recovered pseudocode are analysis observations,

not original source. Provider unavailability and unsupported metadata remain

unknown rather than false.



For a completed `analyze_function` dossier, use `inspect_analysis_view` with

`view: {kind: "native", facet: "value_flow_operations", offset: 0, limit: 32}`

and the exact retained Evidence ID to read selected facts without reanalysis.

Native facets also include procedure, pseudocode, assembly, basic blocks,

comments, callers/callees, references, unresolved calls, referenced strings and

names, the native API record, and value-flow summaries. Pseudocode offsets and limits count UTF-16

code units; use the returned `next_offset` for continuation. Provider limitations

and unavailable facts remain explicit; the complete parent Evidence is retained.



`inspect_macho` on a large framework returns megabytes of imports and exports.

Select `detail: "summary"` for slice identity, UUID and per-collection counts,

then page rows with `view: {kind: "macho", facet: "exports", offset: 0, limit: 64}`

and `normalized_result.parent_evidence_id`. Facets are entrypoints,

architectures, build_metadata, load_commands, dependencies, imports, exports,

segments and provenance. `source_exhaustive: false` means unreturned symbols

may exist.



To see which functions or Objective-C methods a Mach-O actually calls in one

run, use `observe_native_calls` with explicit breakpoints and a bounded

`duration_ms`/`max_events`. It launches a new process under LLDB, so the target

runs and may change files or use the network. Hardened-runtime targets need the

`get-task-allow` entitlement.



Use `binary_session` with no arguments to check the open target, selected

provider, and alignment. Its default `result.tool_availability` carries a

complete inventory grouped by shared facts. Expand each group's `names` and

inherit the inventory-level client requirements unless a group overrides them;

availability, reasons, remediation, modes, and flags remain inline. The

`effects` and `annotations` arrays name true flags from fixed vocabularies, so an

omitted known flag is false. `tools/list` remains the canonical source for full

tool schemas when target or provider state changes.



Provider capability groups carry provider identity and ordered limitations.

Prepend each set's `shared_limitations` to a group's `limitations` to recover the

operation's full ordered list. Candidate capabilities describe possible

providers. Top-level session capabilities describe the current route, and

`analysis_provider_binding` identifies the selected provider.



## Ghidra startup deadline recovery



`provider_timeout` during the first Ghidra query can cover import, auto-analysis,

bridge startup, and readiness. The default 330,000 ms is configurable through

`REA_GHIDRA_STARTUP_TIMEOUT_MS`; a smaller query still needs the same cold import.



Preserve useful Evidence before closing the session or restarting REA. Check

`close_binary` and resolve reported cleanup failures. Set a larger startup budget

in the environment that launches REA, then restart REA and reconnect the MCP

client before reopening the same target. Closing and reopening a binary in the

existing server keeps its original configuration and starts import again.

Environment changes in an agent's shell do not update an already running MCP

server. If its launch configuration cannot be changed, report that constraint

and the exact retry setting instead of claiming a fixed technical limit.



The client's tool-call deadline must allow startup plus the requested query;

server settings and progress notifications cannot override it. CLI analysis

avoids the MCP client deadline, but retains the provider deadline. For example:



```sh

REA_GHIDRA_STARTUP_TIMEOUT_MS=1800000 rea analyze /absolute/path/to/app.exe --provider ghidra --json

```



Thirty minutes is an example budget, not a completion guarantee. Keep host CPU

and memory controls in place. Disable specific expensive analyzers only when

their missing coverage is acceptable and retain the resulting limitations.

Exported C and embedded resources remain useful independent evidence, but a

timeout does not establish complete analysis or absence of code. See the

[deadline and client guide](https://www.google.com/search?q=https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md%23ghidra-first-query-deadlines-and-recovery).



## Static memory and original file bytes



For Ghidra, `read_bytes` reads initialized analysis memory, including loader

fixups; it does not read a running process. Check `returned_bytes` and `complete`

before decoding a table. An incomplete read is missing coverage, not a zero-filled

tail. Use `list_segments` to inspect the selected block's initialization and address-space

facts, and retain unavailable facts as unknown.



Use `address_to_file_offset` to anchor one observed address to original file

bytes. A mapping for the first address does not establish a contiguous mapping

for an entire table, and loader fixups can make analysis bytes differ from source

bytes. Keep source ranges and analysis-memory observations separate.



A pointer table can refer to writable slots populated by a constructor rather

than directly to immutable resources. An uninitialized block or an observed zero

does not establish the slot's later runtime value. Follow `xrefs` and the relevant

writer's assembly or pseudocode; distinguish recorded assignments from inferred

execution order. Do not replace unreadable bytes with zeros or conclude that a

resource is absent without the necessary initialization evidence.



## DOS MZ with Ghidra



For an admitted DOS MZ target, use `inspect_native_load_image` to check measured

loaded bytes, file mappings, relocations and the entry against the immutable

snapshot. Keep `mismatch` and `unsupported` explicit. Verified import covers the

reported static image, not runtime DOS or PC-98 hardware behavior.



For Ghidra decompilation, `procedure_pseudo_code` also accepts `procedure: "file-offset:0x..."`; CLI `rea decompile <path> --file-offset=0x... --provider ghidra` resolves the source byte offset internally. An unresolved 0x-prefixed numeric procedure selector also falls back to a unique file mapping. Existing symbols and analysis addresses win; multiple mappings fail as ambiguous. Preserve the returned file-offset and address locations and raw selection observations. ELF virtual addresses are distinct from file offsets; never assume an arbitrary offset plus image base is an analysis address.



Complete function body ranges use inclusive ends and can contain gaps. Do not

treat the enclosing span as code.

For packed targets, retain the original and separately derived artifact identities;

decompiling an unpacking stub does not recover the unpacked program.



When reading Objective-C dispatch metadata, distinguish class implementation

methods from protocol requirements: class methods report null requirement

flags, while decoded protocol declarations retain required and optional facts.

Property attributes remain raw name/value tokens; use the property's

`atomicity` field for the decoded `N` marker or the default atomic behavior.

Null class/meta flags, ivar counts, atomicity, or read-only values mean the

selected provider did not establish that fact. Symbol names alone do not prove

that a class is a root class or has no ivars.



## Managed PE/CLI



Start with `inspect_managed_artifact`. REA's canonical managed inspection is

execution-free: do not claim it loaded, reflected, executed, or resolved the

assembly. Keep managed/native boundaries and unavailable reconstruction facts

explicit. A bring-your-own reconstruction oracle is separate from the canonical

parser and must not become an implicit setup dependency.



For identity/classification questions, `inspect_managed_artifact` can explicitly

select `detail: "summary"` on the first MCP call. It retains complete metadata

and returns a linked overview with full classification/evidence, nullable

module/MVID, frameworks, metadata coverage/issues/limitations and returned-row

counts. Default complete requests remain unchanged. Read original rows with

`inspect_analysis_view`, source `normalized_result.parent_evidence_id`, and

`view: {kind: "managed", collection: "attributes", offset: 0, limit: 16}`.

Collections are `references`, `resources` and `attributes`. Paging does not

repeat parsing. Returned-row exhaustion

does not prove complete metadata or absence under partial/unavailable coverage;

preserve build-local tokens and their artifact/MVID scope.



`inspect_managed_members` always returns the assembly-wide `member_refs`, even

for one selected type. For questions about a selected type, select

`detail: "summary"` with `type_names`; it returns the selection (with unmatched

names), coverage and per-collection counts. Page rows with

`view: {kind: "managed-members", collection: "call_edges", offset: 0, limit: 64}`

over `types`, `exported_types`, `fields`, `methods`, `member_refs`, `call_edges`,

`field_accesses` or `user_strings`.



### .NET NativeAOT



NativeAOT binaries contain native machine code, so ordinary CIL decompilers

cannot recover the original method bodies. When managed metadata/CIL is absent,

classify that as a native-analysis route rather than claiming source recovery.

Open the native image with the selected deep provider and inspect functions,

strings, calls, and references; describe decompiler output as pseudocode and

inference.



NativeAOT images can be PE/COFF, ELF, or Mach-O executables and shared

libraries. Use file bytes and loader metadata rather than suffixes to identify

them. For packaged apps, inventory/extract with REA's artifact tools and retain

the exact contained image identity. PDB, ELF debug, or dSYM sidecars are

additional evidence only when the provider accepts and matches them.



REA has a built-in read-only snapshot parser for x64 PE targets with .NET 8 RTR

9.1 metadata. An optional headless Ghidra adapter adds database annotations and

broader metadata recovery on Linux; it requires an explicitly configured

NativeAOT JAR. These are separate routes. The built-in parser also runs on

Windows Ghidra P0; read frozen literals from its report, because

`search_strings` does not include them. See the

[NativeAOT guide](https://github.com/morluto/rea/blob/main/docs/ghidra-nativeaot.md)

for setup, supported layouts, and host restrictions. Preserve binary identity

and distinguish derived metadata from Ghidra database observations. Recovered

types and native pseudocode are not original C# source. Windows Ghidra P0 has

no database mutation authority.



## Packages and extraction



Use `inspect_artifact` for application bundles, archives, ZIP/APK/IPA/MSIX/AppX,

ASAR, or DMG inputs when the artifact graph and findings help answer the

question. It returns the complete artifact graph inline. Cite graph manifest

IDs when using them.



For an IPA or a macOS `.app`, ZIP, or DMG, pass the inventory Evidence to

`project_apple_application_graph`. It reports application roots and nested

bundles by path convention: app extensions, XPC services, frameworks, login

items, system and driver extensions, and plug-ins. It also lists privileged

helpers, launchd plists, symlinks, and each bundle's `info_plist_path` and

executable candidates. Roles are path conventions, not parsed plists; read the

listed plists with `inspect_plist`.



After `open_binary` on a `.app` or Mach-O, use `trace_dylib_resolution` to see

which file each `@rpath`, `@loader_path` and `@executable_path` load reaches for

every executable in the bundle. It also lists missing or weak loads and earlier

`@rpath` candidates that are absent. Narrow large bundles with `roots` or

`architecture`. System paths stay undetermined because the dyld shared cache

provides them.



Use `extract_artifact` when materialized files are needed. It extracts the active

target and accepts optional `integrity_policy`; see the [MCP contracts](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md).

It materializes all regular files into a fresh temporary directory chosen by

REA. Symlinks and encrypted entries are inventory facts, not extractable files.

The result reports the materialized directory; callers do not choose the

destination. No separate permission grant is needed.



Native DMG traversal automatically uses a read-only mount on supported macOS

hosts, with an owned temporary mount directory and cleanup. It needs no approval

flag. Unsupported hosts or mount failures remain explicit limitations; do not

claim child inventory when only root identity is available. Extraction is a

separate filesystem-writing operation.



For headerless DOS COM, explicitly open with `format: "dos-com"` (CLI

`--target-format dos-com`). Inspect the load image before trusting function

analysis: the entry is `0x10100`, file offset zero, with imposed real-mode segment

context. PSP/stack/device state remains unmodeled. See [DOS guide](https://github.com/morluto/rea/blob/main/docs/ghidra-dos.md).



For other headerless images (embedded firmware without ELF/Mach-O/PE/MZ

headers), open with `format: "raw-binary"`, `architecture` (`x86`, `x86_64`,

`arm`, `arm64`, `6502`, or `m68k`), and `entry_point` (`0x` hex). File offset 0 is mapped at

that address. Hopper and IDA refuse this interpretation; Ghidra uses

`BinaryLoader` with a generic language: big-endian for `m68k`, little-endian

otherwise. Big-endian ARM, Thumb-only, and Cortex-M variants are unsupported.

`6502` selects NMOS 6502; the entry and complete file mapping must fit within

`0x0000..0xffff`. 65C02, 65816, cartridge containers, bank switching, and mapper

semantics are unsupported. `m68k` requires an even entry and decodes the 68040

superset of the 68000 family; Amiga/Atari containers and vector-table entry

discovery are unsupported. Windows Ghidra P0 admits raw images only for `6502`. See [raw binary guide](https://github.com/morluto/rea/blob/main/docs/raw-binary.md).



### Function annotations in Ghidra



Use `annotate_native_function` for one function name and/or entry comments, with at least one explicit change. Review its annotation readback and refreshed dossier inline. Changes are atomic and session-scoped; empty comments clear them, omitted fields preserve them. Later MCP calls observe edits until close. CLI `annotate-native-function` returns the updated analysis before discarding the session. Original executable bytes are unchanged; edits invalidate immutable snapshots. Windows P0 does not admit database mutations. For naming only, `set_address_name` / `set_addresses_names` also work with Ghidra: they name function entries or data addresses (primary labels) and return compact per-address success booleans instead of a dossier.



## Offline PE resource inventory



Use `inspect_pe_resources` with an absolute `path`, or

`rea inspect-pe-resources ./selected.exe --json`, for portable PE32/PE32+

resource inspection without opening a native target. Preserve returned Evidence:

type/name/language IDs and UTF-16 names, original directory/data/payload ranges,

code pages, payload hashes and static icon-group references. Same-language icon

resolution is explicit; missing references and size mismatch remain visible.

Other payloads are opaque, and this operation does not decode images or simulate

Windows resource loading. Consult the budgets and supported tree profile in

[offline binary diagnostics](https://github.com/morluto/rea/blob/main/docs/binary-diagnostics.md).



For exact core-module import/export differences, use `compare_wasm_interfaces`

with two complete inspection Evidence records (or current-session retained

references) and explicit scope. Preserve unknown types/duplicate names; static

interface equality is not runtime compatibility. CLI accepts complete inline

Evidence in `rea compare-wasm-interfaces input.json --json`.



## Godot PCK



For a standalone PCK, `open_binary` then `inspect_artifact` with

`detail: "summary"` retains the complete static inventory. Use the returned

`parent_evidence_id` with `inspect_analysis_view` inventory occurrences filtered

by exact `logical_paths` or `occurrence_ids`, and join `artifact_id` to nodes

filtered by `artifact_ids`. Select only needed fields; identity links remain.

Prefer `inspect-artifact --detail summary --evidence_output PATH` for CLI tasks;

the same CLI discovers embedded packs via their EOF trailer without opening a

native analysis provider. Normal native opening remains unchanged.



Distinguish declared MD5 from observed SHA-256 and graph/page completeness from

`source_coverage`. Encrypted directories and sparse bundles have unknown entry

coverage; encrypted members have unknown content identity. An empty filtered

page cannot prove absence in unknown coverage. Retained views are historical,

not fresh filesystem checks. No decryption, Godot resource decoding, GDScript

decompilation or target execution is provided. See

[Godot PCK](https://www.google.com/search?q=https://github.com/morluto/rea/blob/main/docs/godot-pck.md).





================================================================================

FILE: .agents/skills/reverse-engineer-anything/https://www.google.com/search?q=references/javascript-applications.md (Reference path: https://www.google.com/search?q=references/javascript-applications.md)

================================================================================



# JavaScript and Electron application artifacts



For captured or bundled JavaScript that needs readable source recovery, use

`recover_javascript_sources` with an absolute `path` and absent

`output_directory`. Supply related runtime/shared/lazy files in

`additional_paths` when advertised, then analyze the returned `analysis_input`

directory together. Each input retains its own snapshot, digest and byte-range

provenance; inputs and recovered code are never executed. Recovery requires a

caller-supplied Wakaru on Linux x64; see [the recovery guide](https://github.com/morluto/rea/blob/main/docs/javascript-recovery.md).



Use `analyze_javascript_application` directly on the operator-supplied ASAR or

extracted tree. When the question concerns known source paths and the connected

schema advertises `source_paths`, select exact inventoried paths such as

`["package.json", "main.js", "preload.js"]`. Include supporting manifests or

source maps explicitly; dependencies are not implicitly analyzed. REA retains

the complete artifact inventory and identity but reads source text and analyzes

only selected files. The result and summary record `source_selection`; files

outside scope and their relationships remain unknown, so partial application

coverage does not mean the selected source failed. Use repeated `--source-path`

on either static application CLI route. Omit the selection when the question

requires complete application analysis; `source_paths: []` is invalid, not an

unfiltered request. `detail: "summary"` reduces delivery

and does not by itself reduce analysis work.



Exact `#alias` specifiers resolve through the importer's

enclosing package `imports` map to package-local files; nested `node_modules`

packages use their own map. Wildcard, recursive, and external-package import

targets stay unresolved with that limitation. When size is unknown or large and the connected schema advertises

`detail`, request `detail: "summary"`. This returns an `inspect_analysis_view`

Evidence record with a distinct ID and a `normalized_result.parent_evidence_id`

for the complete retained application analysis. Source-map contents are part of

that static analysis. Read findings, coverage, limitations and unknowns, then

follow a specific unanswered question. Older servers without `detail` return

the complete application Evidence inline when it fits.



When the connected schema advertises `max_heap_mb` and `analysis_timeout_ms`,

these select the isolated source analyzer's old-space heap and per-source

deadline. Defaults are 1024 MiB and 300000 ms. They do not change the MCP

process heap or the client's tool deadline. For a host timeout without REA

output, use the [deadline recovery guide](https://www.google.com/search?q=connection-and-recovery.md%23distinguish-client-and-server-deadlines)

instead of raising the server budget. A Bun-hosted REA does not enforce the heap choice; on Windows it

instead limits the analyzer's committed memory to that choice plus a 512 MiB

runtime reserve.

Resource-limited analyses preserve completed static facts and

report partial semantic coverage with specific unknown scopes; this does not

mean the source is malformed. Inspect those limits before retrying a source.

When expanded relationships exceed the parent's available memory, inspect the

file's modules item view for retained `static_analysis` and

`semantic_module_analysis`. Their facts remain available even when graph links

are unknown. Cumulative result exhaustion can stop analysis before every file

is examined; the inventory and remaining unknown scopes distinguish that case.

Timeout or cancellation after source analysis begins retains partial Evidence

in the same session. A returned `error.details.partial_observation` reference

can be supplied directly to `inspect_analysis_view`. If the SDK cancels locally, retrieve its recorded ID from

the Evidence bundle before inspecting the partial analysis.



## Read a module without repeating analysis



Use the actual returned parent ID, on the same connection, as `source.evidence_id`.

The following IDs are placeholders to replace with returned values. When the

module's node ID is not already known, page identities before selecting an item.

Pages return only node IDs, paths and roles; choose a useful page size and follow

`coverage.next_offset` when another page matters:



```json

{

  "source": {

    "kind": "retained-evidence",

    "evidence_id": "ev_ACTUAL_PARENT_ID"

  },

  "view": { "kind": "page", "collection": "modules", "offset": 0, "limit": 16 }

}

```



Select the relevant page entry by its exact `node_id` and recorded role:



```json

{

  "source": {

    "kind": "retained-evidence",

    "evidence_id": "ev_ACTUAL_PARENT_ID"

  },

  "view": {

    "kind": "item",

    "collection": "modules",

    "selector": { "node_id": "jag_node_ACTUAL_NODE_ID" }

  }

}

```



Module pages include asset, bundled and source module roles, so one path can

identify several entries. Use `selector.path` only when uniqueness is established;

the returned node ID avoids needing a complete inventory to prove uniqueness. On ambiguity,

select the matching node ID from the page or the error's candidates. Follow

`next_offset` when another page matters. An item exposes that module node's

recorded observations, identity, hashes, exports and source ranges; it does not

include every child syntax observation, related edge or original source file.

An absent item fact is not evidence of absence from the whole application.



For canonical identities and retained source-range counts, use a typed reference

page instead of reading every full item:



```json

{

  "source": {

    "kind": "retained-evidence",

    "evidence_id": "ev_ACTUAL_PARENT_ID"

  },

  "view": {

    "kind": "javascript",

    "collection": "modules",

    "projection": "references",

    "where": { "path": "main.js", "kind": "javascript-module" },

    "offset": 0,

    "limit": 16

  }

}

```



Filters match exact retained strings; omit a filter to include all values, use

`path: null` for unavailable paths, and `path: ""` for a recorded empty path.

Rows preserve canonical `identity` and distinct observation support states in

`basis`. `retained_source_range_count` counts retained source-range observations,

not runtime imports or unique reference sites. Use a row's `node_id` with the item

view above for exact locations and full supporting observations. Follow

`coverage.next_offset`; page exhaustion describes matching retained rows only.

Check `source_coverage` for source selection, partial/unknown graph coverage and

unknown counts before drawing a negative conclusion.



## Trace only the remaining question



Use `trace_application_feature` on the parent application Evidence for one

literal node ID, route, string, API, IPC channel, module, or native export.

Select `incoming` for relationships leading to the seed, `outgoing` for those

leaving it, and `both` when the question needs both. Trace traversal includes

containment relationships, so even a narrow seed can expand many nodes; a

bidirectional trace can reach unrelated sibling modules. A module item or page

is preferable when its observations already answer the question. Do not treat

all reached nodes as participants in the feature.



Reuse retained parent Evidence when the server advertises it, or supply complete

Evidence inline. Include Hopper or Ghidra Evidence only when its artifact digest

matches exactly.



## Recover an oversized display



An oversized response reports `resource_constraint` and

`details.resource: "transport"`. Reuse

`details.reported_limits.evidence_reference` with `inspect_analysis_view` for a

summary, one module, or a stable page of module identities.

`export_evidence_bundle` writes the complete canonical session to a

caller-selected file. These workflows keep the original Evidence and coverage;

a broad follow-up can also exceed framing.



A client can truncate a successful result inside its text envelope without a

REA `resource_constraint`. Treat a truncation notice or incomplete JSON as a

display limitation; do not claim the full record was examined. Reuse the known

parent ID for smaller views, or export complete Evidence to a selected file

while the session remains open. If the parent ID was lost from the preview,

use the prior analysis summary or explicit ledger entries to recover it; do

not invent an ID or rerun analysis just to reproduce the same display.



BrowserWindow preferences, preload and contextBridge surfaces, IPC

registrations, utility processes, and native binding requests are static syntax

observations. Only a unique exact literal IPC channel match supports an inferred

pairing. Dynamic or ambiguous channels remain unresolved. A requested `.node`

member is not a verified native export. Never claim runtime reachability,

registration, defaults, or policy enforcement from static analysis.



For version comparison, analyze each version once, then call

`compare_application_versions`. Accept only its digest, source-map, structural

fingerprint, or non-module semantic matches. Module ordinals and minified names

are not persistent identity. Report added or removed only with complete

opposite-side coverage; otherwise report unknown.



When the question asks how one exact exported callable's returned object shape

changed, analyze each version once and then call

`compare_javascript_export_shapes` with explicit module paths and export names.

Use the returned IDs on the same connection, or complete inline Evidence

records, from both analysis calls. Accept variant

pairing only through the tool's unique exact literal discriminant. Read

`property_inventories` and each change's `presence` before treating `unknown` as

"the name was not observed": inventories list observed property names even when

values stay unknown, with a `source_range` for each paired or unpaired variant.

Array holes and mutation-invalidated slots are not observed properties.

Complete parent coverage reports presence-only

`added`/`removed` independently of unresolved values. Cite the

comparison Evidence and report JSON Pointer changes; dynamic values, ambiguous

variants, and incomplete parent-property coverage stay unknown. This is static

inference, not runtime behavior. When runtime semantics are needed, run

behavioral probes against the relevant application versions and capture them

through the available browser, Electron, or process workflows.



## Reusing application Evidence



When advertised by the connected server, application trace and compare tools

accept complete inline Evidence or

`{"kind":"retained-evidence","evidence_id":"ev_<64 lowercase hex characters>"}`

for their application input (`application`, or `left`/`right`). `inspect_analysis_view`

uses the same retained-reference form in `source`, or portable inline Evidence,

to project a summary, module page, or one module with its recorded observations.

This notation is

a template: replace it with the actual returned ID. Versions before 4.1.0 accept only full

inline Evidence. Use the exact ID

returned by the producer on the same MCP connection. Resolution does not run

analysis or select a provider; findings remain inline. Native observation

arrays still take full Evidence. `close_binary` clears retained references;

export a bundle before closing, or supply portable inline Evidence in another

connection. A missing reference includes its ID and recovery guidance.



For exact file/native metadata or processing gaps, use

`view: {kind: "javascript-facts", where: {paths: ["package.json"]}, property_keys: ["name", "operation", "analysis_status"], limit: 32}`.

Rows retain canonical node/observation identity and original Evidence. Paths

match Evidence artifact-path/source-range locations; missing properties remain

omitted and source coverage stays separate from page exhaustion. Batch paths and

select only needed property keys; complete Evidence remains accessible by export.

If names are unknown, opt into `include_available_property_keys: true`; it lists

the original keys per returned observation without unselected values. Keep each

row's node/observation identity paired when composing facts.

These rows select application-graph observations; semantic relationships and

semantic unknown records remain in the complete parent Evidence and trace tools.





================================================================================

FILE: .agents/skills/reverse-engineer-anything/https://www.google.com/search?q=references/android-applications.md (Reference path: https://www.google.com/search?q=references/android-applications.md)

================================================================================



# Android application artifacts



Use the connected server's advertised Android tools. Repository main and npm

4.1.0 include this family. A skill installation alone cannot add it to an

older server.



Start with `inspect_android_package` on the caller's APK path for package

identity, manifest declarations, coverage, and inline Evidence. Use

`search_android_classes` to find candidates, `inspect_android_class` for one

class's members, `inspect_android_method` for decompilation, and

`trace_android_references` for incoming static references. Each call takes its

own APK path and explicit selectors; do not open a native session first.

Choose an `overload_index` from the class inventory when methods are ambiguous

instead of guessing.



The provider requires a separately supplied headless JADX MCP JAR 0.7.1 and

Java 17 or newer. `REA_JADX_MCP_JAR` selects the absolute JAR path; `JAVA_HOME`

can select Java. REA setup does not install or configure that JAR, and doctor

provider scopes cover Hopper/Ghidra rather than JADX. Use existing tools and

report missing prerequisites for the Android task specifically.



Linux and macOS use the POSIX owned-process boundary. Windows x64 requires the

matching bundled native controls and uses an owned Job Object with bidirectional

stdio. A full JDK, including `jdk.compiler`, is required on every host; Windows

`JAVA_HOME` selects `bin\java.exe`. Consult the Android guide for actual host

verification coverage. Calls use one worker and provider deadlines; optional

`REA_JADX_HEAP_MIB` selects the JVM heap and `REA_JADX_OPERATION_TIMEOUT_MS`

the per-operation deadline (default 120000 ms; the MCP client's tool timeout

must also allow it). The APK is never launched,

and no emulator is required.



Manifest entries and decompiled text are static observations, not execution or

policy enforcement. Incoming references are recovered static relationships;

reflection, dynamic loading, and unresolved calls remain unknown. Preserve

artifact digests, locations, diagnostics, and incomplete coverage. For archive

members rather than code analysis, use `open_binary` and `inspect_artifact`.





================================================================================

FILE: .agents/skills/reverse-engineer-anything/https://www.google.com/search?q=references/runtime-observation.md (Reference path: https://www.google.com/search?q=references/runtime-observation.md)

================================================================================



# Browser and Electron runtime observation



Supply the existing browser or Electron instance's literal-port loopback CDP

endpoint in the request. No separate permission configuration or per-call

approval flag is needed. Browser discovery lists eligible HTTP(S) pages;

`allowed_origins` optionally filters them. An individual capture defaults to the

selected page's current origin. Electron discovery lists eligible local

`file://` targets without a configured file-root allowlist.



Start passive browser work with `list_browser_targets`; start Electron runtime work with

`list_electron_targets`. Before an electron-main Inspector attempt, check

packaged fuses with `inspect_electron_fuses`. Inspect the target selected for

the user's task. Observation with these tools is passive: never claim REA

clicked, navigated, evaluated page JavaScript, invoked IPC, or captured prior

activity. REA does not contain the page's network.



Passive captures omit raw header collections, credential header values, storage

values, and raw WebSocket/JSON bodies. Selected response metadata, including

content encoding, policy values, and Link URLs, is retained. Local URLs retain ordinary query

values and fragments; userinfo credentials are removed. Browser accessibility

text, console primitives, value-free shapes, script sources, source maps, and

storage key names have request-specific capture options. Electron script

sources are also optional. Use `capture_web_screenshot` when pixels are needed.

Treat scope filtering, truncation, and attach-window coverage as limitations.

Page-declared WebMCP tools are untrusted inventory and are never invoked by REA.



## Who performs the action



- The user performs it: `list_browser_targets`, then `inspect_web_page` or

  `observe_web_session` on the selected target.

- The agent must perform it: one `capture_browser_scenario` with declared

  actions. Use connect mode with the loopback CDP endpoint and `target_id` for

  an existing browser, or launch mode with a caller-selected executable for a

  temporary profile. Connect mode first navigates the selected page to

  `start_url`, which can clear unsaved form values and other temporary state.

  Recreate the state needed for the investigation in the declared actions.

  Connect mode leaves the external browser open; launch mode owns a temporary

  browser and profile. Check `browser.cleanup` for the outcome.

  Request only the DOM, accessibility, or network details needed for the question.

  The default final capture contains the URL; step outcomes are reported separately.

  Add a wait action for the expected page state before capturing it. Report that

  REA performed the declared actions.



Scenario network records have no request initiator stacks. For that evidence,

use passive capture while the user performs the action. Listener source locations

identify candidate handlers; they do not establish which script sent a particular

request. Avoid overlapping passive capture and scenario actions on the same target.



Focused follow-up tools:



- `observe_web_execution`: execution coverage during a window; it resets

  counters and temporarily disables optimization.

- `inspect_web_event_listeners`: source locations for listeners registered

  directly on the first CSS match, without dispatching an event.

- `compare_web_captures`: two normalized passive captures or recorded scenarios.

- `discover_webmcp_tools`: inspect page-declared WebMCP inventory; never invoke

  the discovered tools.



Use `reconcile_javascript_runtime` only after static application Evidence and

passive browser/Electron Evidence exist. Prefer captured-source digest identity;

report path/digest disagreement as a mismatch and preserve ambiguity. Explicit

path mappings are inference inputs and never broaden filesystem or CDP authority.

A bundle observed at runtime does not prove every contained module executed.



## Fiddler Everywhere traffic debugging



For large saved captures, request `detail: "summary"`, then page retained Evidence

with `inspect_analysis_view` and `view: {kind: "capture", detail: "preview", offset: 0, limit: 20}`.

Select complete record pages only for needed headers, metadata or payloads; views

read the historical parent without repeating capture decoding.



For selected protobuf/gRPC bodies, keep raw bytes as the source and use

`inspect_analysis_view` kind `protobuf`, collection `bodies`, `frames` or

`fields`. Batch exact record ordinals and field numbers/IDs, and select

`schema_value` or `text` only when needed. Supply a local descriptor set and

message type for schema interpretation; compressed payloads remain unknown.



Inspect native `.saz` snapshots with `inspect_web_network_capture` and

`format: "saz"`; encrypted archives are unsupported. For live

traffic analysis, connect Everywhere's separate MCP server and use its

advertised session tools with an explicit `sessionsSource` (`LiveTraffic` or

`AgentCalls`). Preserve existing sessions and filters when inspecting a

recorded run. See the [capture and MCP guide](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md)

for the workflow and Telerik's public setup and traffic-debugging skills.





================================================================================

FILE: .agents/skills/reverse-engineer-anything/https://www.google.com/search?q=references/evidence-workflows.md (Reference path: https://www.google.com/search?q=references/evidence-workflows.md)

================================================================================



# Evidence, comparison, and verification workflows



Evidence-producing tools return the complete Evidence record directly in MCP

`structuredContent` and CLI JSON. Read `normalized_result` for operation data,

and cite `evidence_id` when another tool or your explanation needs a stable

reference. Preserve authority, limitations, coverage, and residual unknowns. If a result

is incomplete or paginated, continue only when the remaining data matters to

the task; do not fetch a bundle or resource merely to read a result already

returned inline. When complete `inspect_binary_layout` or

`analyze_javascript_application` Evidence is already retained, call

`inspect_analysis_view` for a summary, one section/symbol/module, or a stable

page instead of repeating the producer.



Completed `inspect_artifact` inventory also supports a summary and

`view: {kind: "inventory", collection: "occurrences", logical_paths: ["package.json", "main.js"]}`.

Omit `logical_paths` to page all available occurrences; `[]` selects none.

Other inventory collections are `nodes`, `edges` and

`integrity_contradictions`. Keep `source_complete` separate from page exhaustion:

a missing match in partial source Evidence does not establish absence. Use the

returned parent Evidence ID for subsequent views and export before closing the

session when the source must survive it.

When `tools/list` advertises `inspect_artifact.detail`, request `"summary"` to

retain its complete source and receive that view immediately. Without that

advertised choice, keep the existing complete call. CLI inspection returns

portable complete Evidence; save it before projecting a selected inline view.



For native procedure/name/string inventories, select `detail: "summary"` when

the connected tool advertises it and the task needs counts or selected rows.

Use its parent Evidence ID with

`view: {kind: "native-inventory", offset: 0, limit: 32, fields: ["value"]}`.

Search tools retain the existing pattern/mode/case/document selection. Omit

`fields` for complete records; `record.address` and `source_index` remain on

selected rows. Selecting `value` keeps its string/decoding qualifications.

Parent Evidence ID plus source index preserves same-address

alternatives. Follow `coverage.next_offset` only as far as the question needs;

exhausting retained rows does not establish complete program discovery.



Use `record_unknown` to track unresolved questions in the user's investigation

and name the authority or environment still required. Supply supporting and

contradicting evidence IDs. It updates the session registry directly.

Use `update_unknown` with the current revision; reread after a stale revision

instead of retrying blindly. Only qualifying observed evidence can verify a

resolution.



Use comparisons with complete, compatible page sets when claiming equivalence

or absence:



- `compare_artifacts` compares inventory pages by occurrence path, content,

  metadata, and graph relations.

- `compare_functions` compares explicit function Evidence, not fuzzy

  whole-binary matches.

- `compare_bundles` compares canonical bundle membership and unknown history.

- `find_changed_behavior` combines existing comparisons; static differences

  remain candidates, not causal proof.

- `build_call_path` needs explicit function dossiers from one artifact/provider;

  an incomplete frontier makes absence unknown.

- `correlate_static_and_runtime` uses explicit mappings; matching patterns are

  hypotheses, not causality.

- `verify_reconstruction` evaluates a finite typed specification. A pass covers

  only declared comparable claims, not global equivalence.



Process captures are opt-in behavioral evidence, not a security sandbox. V3

captures cannot be upgraded to V4; rerun the original scenario. Distinguish root

exit from descendant settlement and require freshness when the task needs it.

A timed-out target that must write a final report needs `finalization_ms`: REA

sends SIGTERM to the captured root, keeps observing, and sends SIGKILL once

only if the target has not exited by the end of the interval.

`exit.finalization.signals` lists each attempt with its delivery result; the

observed exit signal stays in `exit.signal`, `exit.code` is null for every

deadline exit, and the code of a finalizer that exited on its own is in

`exit.finalization.exit_code` (null on a signal exit or when no exit was

observed).



Use `inspect_analysis_view` with `view: {kind: "api-surface"}` on retained

`inspect_web_network_capture` HAR Evidence to group observed request lines by

method, origin and path template. Format matches are inferences, not handler

identity or schemas. Group pages cite parent record ordinals; consult record

coverage and exclusions before claiming completeness. No requests are replayed.

When the connected schema advertises `include_query_parameter_names`, select

it in the view for distinct observed names with original record ordinals. Query

values are omitted; the names establish neither required parameters nor a

complete server schema. Keep the original parent Evidence for exact URLs.



Use `inspect_analysis_view` with `view: {kind: "environment-manifest"}` on the

same retained HAR Evidence to project the primary origin's request lines into

named tools with path templates, parameters, observed query names, value-free

body shapes and record pointers for an agent environment. Opt into

`template_rules` only when recorded identifiers need them; every template,

parameter and merged sibling is an inference, no header, cookie or body value is

copied, and the three stated unknowns stay unresolved.



Use `view: {kind: "environment-state"}` with the manifest's `template_rules` to

extract the data those reads observed instead: entity types and identity

fields, entities with recorded values, documents, and per-tool render plans

checked against the recordings. The state comes only from reads before the

first related write; types, identity and list membership are inferences.





================================================================================

PART 2: REPOSITORY & MAINTAINER AGENT GUIDELINES (AGENTS.md + rea-* skills)

Included verbatim for working on or maintaining the REA repository itself.

================================================================================





================================================================================

FILE: AGENTS.md

================================================================================



# Repository Guidelines



## Product and Authority



REA is a local-only reverse-engineering tool with shared CLI/MCP workflows. Distinguish observations, derivations, inferences, and unknowns; preserve Evidence provenance and session semantics through both adapters. Provider support and setup live in [README.md](https://www.google.com/search?q=README.md%23choosing-a-deep-analysis-provider) and its linked guides.



Follow the [contribution scope and fail-closed integration rule](https://www.google.com/search?q=CONTRIBUTING.md%23contribution-scope). Do not integrate capabilities while material scope, authority, side-effect, or required verification questions remain unresolved. For new providers or capabilities involving target execution, injection, mutation, or protection recovery, seek the required maintainer scope decision before substantial implementation for integration. Welcome early proposals, small exploratory prototypes, and draft PRs that help resolve questions; they do not authorize integration.



Ghidra uses ephemeral databases without modifying executable bytes or controlling a GUI; Windows Ghidra P0 has no mutation authority. IDA analysis is read-only; never save or close an attached GUI database.



Configuration changes must be additive and idempotent, with backups. Installers must not install or upgrade unrelated software, including Homebrew, Node.js, npm, Java, or Ghidra. Ghidra and IDA are bring-your-own. `rea setup` must show its planned changes and require approval before writing files or installing Hopper.



Preserve caller-selected inputs and local evidence, including output, URLs, paths, digests, and metadata. Redact transport authentication credentials and explicitly marked sensitive values; do not infer secrecy from names or text patterns. Do not persist the ambient environment merely because a child inherits it.



## Architecture and Cleanup



Dependencies flow inward: domain semantics and contracts, provider adapters, shared application workflows, then CLI/MCP adapters. Keep engine protocols and provider-specific code out of domain/application layers. See [docs/architecture.mermaid](https://www.google.com/search?q=docs/architecture.mermaid) when changing composition.



Give each interpretation and resource a clear owner. Consumers must use that owner's parsed facts rather than reinterpret raw source. Preserve identity, omission, uncertainty, and source evidence across boundaries. Retain ownership of resources whose cleanup failed. Reuse `src/process/` supervision and identity primitives; a PID and executable path alone do not establish ownership after exit or reuse.



Keep proof of ownership separate from validity, editability, and readiness. Malformed owned data may still be safely removable. Unresolved identity or applicability must remain unknown rather than be treated as absent, foreign, or aligned.



For lifecycle changes, follow [ownership and completion invariants](https://www.google.com/search?q=docs/tool-design.md%23own-the-lifecycle) and select the applicable [lifecycle regressions](https://www.google.com/search?q=docs/testing.md%23lifecycle-regressions). Include late handshakes, cancellation during final cleanup, mixed child outcomes, and cleanup retry where those stages exist; active-execution cancellation alone does not cover finalization.



Assess brittleness in touched code during implementation, debugging, review, and maintenance. Fix the producing representation or ownership rule before adding downstream repairs. Normalize once at the owning boundary using format-aware parsers. Remove superseded representations, aliases, wrappers, and redundant tests after verifying affected consumers. Introduce abstractions only when they remove observed complexity.



When fixing a bug, inspect the producing boundary and affected consumers for duplicated interpretation or unclear ownership. Complete any directly related refactor in the same change and remove superseded code. Passing regression tests alone does not establish that the brittleness is resolved. If related cleanup remains, explain what remains and why.



When addressing a review thread, inspect the producing boundary and affected consumers for brittleness. Complete directly related refactoring in the same change. Before resolving the thread, explain the root cause, structural fix, validation, and any remaining cleanup.



Parse unknown boundary values and model expected failures with the tagged error algebra and `Result`. Preserve partial facts and meaningful failure reasons. Keep identity and lookup values separate from display formatting; preserve source values and explicit unknowns when normalization loses information. Absolute paths, file URLs, and HTTP paths have different semantics.



Validate advertised JSON Schemas after SDK conversion against their declared dialect and actual clients. Bind handlers to named contracts with exact types; catalog ordering must never select an operation or schema.



## Performance



Design analysis workflows and agent interfaces for efficiency from the first

implementation. Correctness, useful answers, Evidence provenance, caller choices,

compatibility and safe resource bounds remain required.



Optimize in this order:



1. Agent tokens and context. Return the smallest sufficient answer with

   necessary provenance, coverage and limitations. Use task selection,

   summaries, paging and retained Evidence where supported; honor requested

   detail and keep complete Evidence accessible. Count the whole task,

   including schemas, extra calls and retries.

2. Analysis time. Reuse validated results and shared work. Cache keys must

   cover result-affecting inputs; define invalidation and lifetime. Validate

   freshness before reporting cached live state as current.

3. CPU and memory. Avoid unnecessary work and copies; bound concurrency,

   retained state and serialization growth.



For changes affecting these costs, measure representative completed tasks and

compare equivalent workflows before and after where available. Report token

usage, elapsed time, CPU time and peak process-family memory. Separate cold

and warm runs, label estimates, and state unmeasured costs. Fewer bytes alone

do not establish fewer tokens or faster analysis.



## Development



Use [.nvmrc](https://www.google.com/search?q=.nvmrc) and `package.json#packageManager` for the pinned toolchain. Cursor Cloud may place older Node.js first on `PATH`; environment setup installs the pinned toolchain under `/usr/local/bin`.



- `npm ci`: install locked dependencies.

- `npm run build:cached`: build the runtime and packaged skill.

- `npm run test:local -- PATH...`: source tests without building.

- `npm run test:focused -- PATH...`: exact tests with their required artifacts.

- `npm run check:fast`: cached typecheck/lint and the pre-push check.

- `npm run docs:check`: validate generated documentation.



Use relevant checks for the change. The complete local gate, `npm run check:pr`, is optional for broad changes or CI diagnosis. See [CONTRIBUTING.md](https://www.google.com/search?q=CONTRIBUTING.md) for development, generated-file ownership, and release conventions.



`docs/public/product-catalog.json`, `docs/verification/managed-conformance-*.json`, and `skills/` are ignored outputs. Edit source contracts and `.agents/skills/reverse-engineer-anything/`, then regenerate as needed. `.cache/mcp-tool-catalog.json` is test metadata; runtime builds and source checking do not consume it. Never commit binaries, provider project documents, credentials, `dist/`, `node_modules/`, or local planning artifacts.



## Tool and Test Changes



For tool design, follow [docs/tool-design.md](https://www.google.com/search?q=docs/tool-design.md): start from the analyst question, reuse existing contracts, preserve caller choices, and return useful evidence inline. Limits must follow real format, protocol, authority, or resource constraints. Account for representation expansion before allocation; derive completeness from examined coverage.



For test changes or provider claims, use [docs/testing.md](https://www.google.com/search?q=docs/testing.md). Prefer real public CLI/MCP workflows, then production-boundary integration, then producer goldens. Keep module tests for distinct semantics stronger workflows cannot reliably reproduce. Preserve malformed-input, cancellation, cleanup, permission, capacity, and target-identity coverage when pruning. Report unverified coverage explicitly; simulated providers do not establish real-provider behavior.



Use Conventional Commit subjects and PR titles. Mark breaking changes with `!` or a `BREAKING CHANGE:` footer. Describe behavior changes, relevant validation, and real-provider verification scope.



## Issue Reports



Follow [issue reporting guidance](https://www.google.com/search?q=CONTRIBUTING.md%23reporting-issues) and the matching

issue form. Keep reports concise and cite the smallest useful evidence.

Distinguish observed results, source-derived reasoning, hypotheses, and proposed

checks. Never claim runtime reproduction or measurements you did not perform.

Use `NOT_ENOUGH_INFO` with an explanation for missing narrative answers or evidence.

Incomplete reports, source-only findings, and early feature or design ideas are

welcome when their limitations are explicit; a completed diagnosis or fix is not

required to open an issue.



## Pull Request Readiness



Follow [human ownership and readiness](https://www.google.com/search?q=CONTRIBUTING.md%23pull-request-ownership-and-readiness)

when preparing a PR. AI-assisted contributions are welcome; a human must review

and own the final diff, check the validation evidence and its limitations, and

explicitly declare the PR ready for initial maintainer review.



Keep the PR body concise and current, with the concrete problem, observable

outcome, approach, and evidence. Report only checks that actually ran as executed;

distinguish source-derived conclusions, proposed checks, and unavailable coverage.

Address actionable automated review findings and explain disagreements.



Leave the template's **Author readiness** declarations unchecked for the human

owner to complete. Never attest to human review on their behalf. Keep the PR in

draft until the human declares the PR initially ready. Later pushes do not

invalidate that declaration or require another human sign-off. Keep the PR body

and affected validation current as work changes. The readiness check validates

the filled declaration; CI and automated review results do not establish that

human review occurred, maintainer scope approval, or merge permission.



&lt;!-- BEGIN:turborepo-agent-rules --&gt;



# This is NOT the Turborepo you know



Turborepo configuration, task behavior, and CLI commands can vary between installed versions and may differ from your training data. Resolve the `turbo` package from this file's directory or relevant workspace; in monorepos, it may not be visible from the repository root. For example, run `node -p "require.resolve('turbo/package.json')"` from a workspace that depends on `turbo`.



Read `docs/README.md` inside that installed package first, then read the relevant pages from its `docs/` directory before changing Turborepo configuration or commands. Heed deprecation notices. These bundled docs match the installed package version and are available without network access.



This block is written and re-added by `turbo` before repository-scoped commands when an AI agent is detected. In the Turborepo source repository, its template is defined in `crates/turborepo-cli/src/cli/agent_guidance.rs`. Removing the managed block while updates are enabled means a later qualifying invocation will add it again. Set `"agentGuidance": false` in the root `turbo.json` or `turbo.jsonc` to opt out; this does not remove an existing block. Keep the block committed with your work to avoid an uncommitted change on the next agent invocation.

&lt;!-- END:turborepo-agent-rules --&gt;





================================================================================

FILE: .agents/skills/rea-analysis-optimization/SKILL.md

================================================================================



---

name: rea-analysis-optimization

description: Optimize REA providers and shared analysis workflows for agent context, latency, CPU, and memory while preserving correctness and Evidence. Use for analysis bottlenecks and cache or query design; CI/test-suite optimization belongs to rea-ci-tests-audit.

---



# REA analysis optimization



Find a concrete source of unnecessary work, change it at its owner, and verify

equivalent completed investigations. A useful outcome can also be a measured

decision to leave an implementation alone.



Follow the checkout's \[suspicious link removed\],

\[suspicious link removed\], and

\[suspicious link removed\]. This skill supplies an optimization

workflow, not additional permission to execute targets, publish, or merge.

Use the current contracts, provider prerequisites, and user authorization.



Read [the Kuna case study](https://www.google.com/search?q=references/kuna-case-study.md) when selecting a

reuse strategy or interpreting a benchmark. Its pinned observations illustrate

tradeoffs; they are not current-provider guarantees or universal speedups.



## Pin the question and the correctness oracle



Describe the analyst's completed task, including the facts and relationships

needed to answer it, requested detail, source access, and meaningful unknowns.

Choose a representative real artifact and a small or empty case. Record the

baseline revision, target digest, engine identity, options, host, and entrypoint.

Use a separate checkout for changes without disturbing other work.



Establish an oracle independent of the changed implementation: source-built

fixture expectations, independently mapped file bytes, or a native producer

paired with checks of its interpretation. Comparing two wrappers around the

same faulty decoder does not establish correctness. Preserve address widths,

same-address alternatives, unresolved endpoints, coverage, and source linkage.

An empty result proves absence only within the actually examined scope.



## Locate the earliest unnecessary work



Trace one public CLI or MCP task through shared application code to its producer.

Measure relevant phases: admission and identity checks, native analysis,

decoding, lookup, projection, serialization, Evidence retention, and cleanup.

Include catalog discovery and extra calls when they affect the completed task.



Use the evidence to choose the smallest structural correction:



| Observed cost                     | Candidate correction                                       | Condition to establish                                                               |

| --------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------ |

| Repeated scans of validated facts | Reuse existing order or lookup structure                   | The owner establishes ordering and identity; every matching alternative survives     |

| Repeated equivalent engine work   | Share a validated result or in-flight producer             | Inputs, freshness, lifetime, and per-caller outcomes remain explicit                 |

| Full reports for selected facts   | Push selection or projection to the earliest capable owner | Required facts and evidence remain reachable; examined coverage is reported          |

| Large temporary transport buffers | Decode incrementally or use bounded source reads           | Validate the whole admitted document; retained facts and copies still consume memory |

| Many repeated homogeneous reads   | Share admission, decoding, or batch work                   | Preserve item identity, order where required, and individual failures                |



Do not introduce an index, generic cache, batch endpoint, or orchestration layer

without identifying the work it removes and its maintenance/resource cost.

Projection after materializing a full report may reduce output while leaving

analysis time and peak memory unchanged. Fix missing or incorrect facts before

benchmarking an alternative composition against a better-covered workflow.



## Keep one interpretation and a defined reuse lifetime



Let the producer boundary validate and normalize facts once. Consumers query

that representation through the shared CLI/MCP implementation; adapters should

not rebuild relationships or independently reinterpret raw reports. Keep lookup

identity separate from display formatting. Reuse contracts when their intent

matches, honoring requested detail and complete Evidence access.



For every cache or shared producer, state its key, owner, invalidation, retained

size, and lifetime. Account for result-affecting target bytes, engine contents,

analysis options, architecture/load mapping, and parser/schema versions where

they affect reuse. Validate live state before calling a cached observation

current. Cache a refusal only when it is deterministic for that validated key;

malformed, partial, transient, or cancelled attempts need explicit retry policy.



One cancelled waiter must not invalidate a successful peer. Preserve producer

failure context and each caller's cancellation reason. Retain ownership and

capacity charges until shared work and cleanup settle; preserve completed

observations when cleanup fails. Exercise invalidation, concurrent consumers,

last-waiter cancellation, close, and cleanup retry when those paths change.



Bound the process family and retained state, not just a parent heap or worker

count. Account for decoding and serialization expansion before allocation.

Choose CPU, memory, concurrency, and disk limits from the host and workload;

stop before OOM and verify owned cleanup. A guard-stopped task is incomplete.

Do not replace a transport buffer cap with an unbounded retained inventory or

hide partial results behind a success status.



## Compare completed tasks and limit the claim



Run the affected real public workflow before and after with equivalent inputs,

results, coverage, and Evidence semantics. Include small inputs so setup costs

and regressions are visible. Distinguish fresh sessions, warm runtime caches,

and OS file caches. Alternate or repeat runs when variance affects the decision.

Choose meaningful boundary regressions for cases the actual engine cannot

reliably reproduce; a fake engine does not qualify a real provider.



Report task outcome, relevant phase timings, total elapsed and CPU time, peak

process-family memory and its accounting method, resource stops, and cleanup.

Check the payload exit status as well as the profiler's. Keep failed attempts

and identify unmeasured costs; a passing retry does not explain a failure.



For token claims, count schemas/discovery, arguments, replies, retries, and

continuations needed to finish the task. Label tokenizer estimates separately

from actual model usage and record the client/catalog behavior. Smaller JSON

alone establishes neither fewer model tokens nor better investigation quality.

Do not claim a complex-software advantage without completed representative

investigations and comparable correctness/coverage.



Finish with the bottleneck, owning change, preserved semantics, executed

checks, before/after measurements, and remaining limits. Keep any integration

record current with its tested revision and distinguish merged production work

from experiment-only code. Stop when the demonstrated bottleneck is resolved

or further benefit remains speculative.





================================================================================

FILE: .agents/skills/rea-analysis-optimization/https://www.google.com/search?q=references/kuna-case-study.md

================================================================================



# Kuna: reuse before adding machinery



Read this reference for concrete examples of the skill's decisions. The records

below concern static Linux analysis with caller-supplied Kuna. They do not

establish parity with another provider or a general advantage for Code Mode,

atomic tools, or any particular orchestration design.



## Exact-address lookup: a measured, narrow improvement



[PR #4695](https://www.google.com/search?q=https://github.com/morluto/rea/pull/4695) reused the validated string

inventory's numeric address order. Previously, each `list_strings(address)`

filtered all cached facts. The owner now performs a binary lower-bound lookup

and returns every encoding at that address: O(log n + matches), without a

second retained lookup index.



The owning implementation is

\[suspicious link removed\], consumed

by \[suspicious link removed\]. Inspect

their current versions before adapting the example. Numeric u64 addresses,

same-address encodings, duplicate rejection, source digests, caller selection,

and the existing session lifetime were part of the contract. Full listings and

literal/regex searches kept their semantics. An attempted removal of the

duplicate-detection set was dropped: no stable memory benefit was established,

and it delayed malformed-input rejection.



### Recorded workload and results



The benchmark used unmodified Kuna 1.833 and LLVM 16 on Linux x86-64, with

602,544 string facts. Baseline was `be0b2d138`; the final feature was

`5f564962da0e1b17f00a68a74a312539f0209a01`, subsequently integrated in

`c6b62754b095a134d6d67877508fa34311a2eda2`. These are historical observations,

not a benchmark of every subsequent main revision.



The same production stdio MCP task discovered the catalog, opened the binary,

made one cold selected read and 28 warm exact reads, checked retained Evidence,

and closed the session. Five selected addresses and two absent selectors were

read four times. A native filtered scan selected the strings; an independent

ELF load-header mapping checked the source bytes and terminators. Returned

facts, source linkage, target digests, and cleanup were checked.



Three alternating fresh sessions per implementation used one CPU, a 4 GiB

process-family hard limit, a 3 GiB early stop, and no swap. OS file caches were

warm. Whole-harness costs include the independent native oracle, hashing,

catalog/client work, and correctness checks.



| Median                                   |     Before |      After |

| ---------------------------------------- | ---------: | ---------: |

| 28 warm exact MCP reads                  |   495.2 ms |    90.8 ms |

| Cold selected MCP read                   |    11.30 s |    11.01 s |

| Whole harness elapsed                    |    28.24 s |    27.43 s |

| Whole process-family CPU                 |    27.71 s |    26.89 s |

| Kernel family peak, including file cache | 2237.6 MiB | 2240.6 MiB |



Warm totals ranged from 491.7–544.3 ms before to 84.8–99.5 ms after: about

5.5 times faster at this phase. Cold/whole-task timing and memory overlapped;

no stable improvement in those costs was established. One small SQLite pair

(7,985 facts) measured 20 warm reads at 88.6 → 80.5 ms and the whole harness at

13.68 → 13.94 s. The large-inventory lookup benefit does not generalize to a

whole-task speedup on small inputs.



Catalog hashes, call counts, and normalized facts were unchanged. A

`cl100k_base` estimate over one pass of raw catalog JSON, arguments, and replies

was about 846,000 tokens in both lanes, with about 802,562 from the catalog.

This was transport serialization, not rendered model context or actual usage;

client discovery, prompts, replay, and protocol framing were unmeasured.

**No token reduction or improved agent investigation outcome was established.**



Pinned target SHA-256:

`f62d254b7f2bf42df8c8b07d46ee3bb4c2cafeca436b2e6bc6ccbe4581f58f40`.

Pinned engine SHA-256:

`d858918b0766435cd96b999a77f2d5a31a0cc4f07256421c883b5b9dc4dd58e4`.

All six normalized-result sequence digests were

`4d2f90269da8568984090b20274163c4a7c2a0538aab63530bd2fe44840a0bba`.

Selected byte agreement does not prove native discovery completeness; missing

strings and relationships can remain unknown.



## Other transferable changes and their limits



- [Cached string inventory and search, #4095](https://www.google.com/search?q=https://github.com/morluto/rea/pull/4095):

  share validated facts across queries in a defined session. Audit key inputs

  and lifetime before extending reuse across targets or engine revisions.

- [Shared single-function work, #4045](https://www.google.com/search?q=https://github.com/morluto/rea/pull/4045)

  and [repeat-request reuse, #4169](https://www.google.com/search?q=https://github.com/morluto/rea/pull/4169):

  avoid duplicate native work while retaining per-caller cancellation and

  cleanup ownership. A query count alone cannot reveal duplicate subprocesses.

- [Streamed strings, #4318](https://www.google.com/search?q=https://github.com/morluto/rea/pull/4318)

  and [streamed call graph, #4329](https://www.google.com/search?q=https://github.com/morluto/rea/pull/4329):

  remove fixed aggregate transport-buffer failures through incremental parsing.

  Streaming transport does not bound every retained object or final reply.

  These links establish changes; no numerical speedup is asserted here.



Typed reference facts, native string-query projection, and shared native byte

reads remained experimental at the 2026-10-17 checkpoint

`65f2f9a22bc892f61d2b00f9a4611124f57d4bff` on

`experiment/atomic-codemode-20261016`. Some experiments used a patched native

engine. Check current integration and bring-your-own engine capabilities before

proposing them; a working experiment is not a stock-provider guarantee.



## Applying the reasoning elsewhere



For another provider or format, inspect its actual representation and native

capabilities before borrowing the implementation. Existing numeric ordering

may support range reads; an on-disk native query may avoid materializing an

inventory; an immutable parse may support several views. Measure the relevant

alternative rather than requiring every provider to use Kuna's cached array.



For live observations, immutable artifact caching rules are insufficient:

validate the process/session identity and freshness required by the caller.

For compact replies, preserve access to source Evidence and report examined

coverage; projection must not silently turn an unresolved edge into no edge.

For batching, test mixed successes and failures and measure the entire task,

including discovery, extra calls, native work, and serialization.





================================================================================

FILE: .agents/skills/rea-analysis-optimization/agents/openai.yaml

================================================================================



interface:

  display_name: "REA analysis optimization"

  short_description: "Optimize analysis with preserved Evidence and measured costs"

  default_prompt: "Use $rea-analysis-optimization to find and verify a concrete analysis bottleneck while preserving correctness and Evidence."





================================================================================

FILE: .agents/skills/rea-changelog-update/SKILL.md

================================================================================



---

name: rea-changelog-update

description: Prepare or rewrite REA release changelogs and GitHub release notes from pinned Git history, with verified contributor thanks and Release Please synchronization.

---



# REA changelog update



Use this for release-note preparation and contributor attribution. Read

\[suspicious link removed\] from the repository root for

publication authority and the existing checkpoint checks. This skill prepares

notes; it does not authorize merging, tagging, or publishing.



## Inventory before prose



Fetch complete history and tags. Select the published baseline tag from

`.release-please-manifest.json` on the release PR's **base branch**, and pin that

branch's exact SHA as the editorial target. REA tags are `rea-agents-VERSION`.

Use the proposed version, including its prerelease suffix; do not change the

`always-bump-minor` strategy to imitate OpenClaw's calendar versions.



```bash

node scripts/release-notes.mjs inventory \

  --repository morluto/rea --base rea-agents-PREVIOUS \

  --target FULL_BASE_BRANCH_SHA --version VERSION \

  --manifest /tmp/rea-VERSION.contributions.json

node scripts/release-notes.mjs record \

  --manifest /tmp/rea-VERSION.contributions.json \

  --summary \

  --output /tmp/rea-VERSION.record.md

```



Read the inventory, not just the existing bot draft. It includes side-branch

commits, GitHub-associated PRs whose merge commits are in the range, commit

authors/co-authors, and confirmed closing issues with their reporters. GitHub

connections are paginated. Network errors stop generation; rerun into a new

output file after recovery. Existing output files are never overwritten.



Unresolved commit identities are retained as names/emails with `user: null`;

never guess a handle or thank the merger as a substitute. The report preserves

unknowns. This is a reviewed metadata snapshot, not independent proof that a

human authored a patch. For unattributed identities, unusual merge strategies,

backports, reversions, or references that GitHub did not associate, inspect

the source PRs and diffs and report the limitation. The current collector uses

confirmed PR-closing relationships for issue-reporter credit; unrelated issue

mentions are not automatically credited. Do not claim that merely inventoried

work still ships after a revert.



## Write for users and retain credit



Rewrite only the newest `## [VERSION]` section in `CHANGELOG.md`, preserving its

version/date/link heading. Use single-line Markdown list items under:



- `### Highlights`: a few release-defining user outcomes; no quota for small releases.

- `### Changes`: capabilities and meaningful behavior changes.

- `### Fixes`: reliability, correctness, compatibility, and safety fixes.

- `### ⚠ BREAKING CHANGES`: retain when applicable, with migrations and original

  PR/commit references required by the existing checkpoint validator.



Group related work by analyst workflow or user impact. Explain the resulting

behavior in short, concrete entries. Highlights summarize the release; avoid

repeating their full descriptions in Changes. Internal cleanup, tests, CI, and

routine documentation generally belong only in the provenance file. Read ambiguous PRs/diffs before making

claims. Distinguish simulated-provider checks from real-provider verification.



Credit each represented contribution once in the public notes with its link

and `Thanks @...` for its verified human author, known co-authors, and confirmed

closing-issue reporters. Grouping preserves all those credits in one line.

When Highlights, detailed entries or migrations reference the same work,

put its thanks in one of those entries, not all of them. Include issue links.

Direct-commit bullets carry the commit link and known human credit.

Exclude GitHub bots and known agent accounts. REA's observed Anthropic, Cursor

and Codex co-author trailers resolve to `@claude`, `@cursoragent` and `@codex`

with GitHub type `User`; the credit policy excludes them while retaining their metadata.

At the REA maintainer's request, omit `@morluto` self-thanks while preserving

authorship in the inventory. Other human contributors remain eligible.

Use explicit GitHub links for cross-repository references to avoid ambiguous

`#NNN` numbers. Unknown handles stay unknown; they are not fabricated credit.



Append the generated `record --summary` provenance link verbatim at the end

of this release. The linked inventory accounts for every discovered in-range

PR and direct contribution, including internal work omitted from the prose.

Do not paste the full `record` output into public notes: it duplicates thanks

and obscures the user-facing changes. Full records remain available for review.

Do not hand-edit generated credits to make validation pass. Refresh the inventory

when product history changes; a prose-only correction can reuse the snapshot.



## Finalize with Release Please



Before changing the live release PR, have authorization for that PR update.

Local preparation and validation can proceed independently.



1. Add `rea:release-notes-finalized` to the selected open release PR **before**

   editing its branch/body. Main proposal pushes respect this label. This is

   our workflow guard, not Release Please's `autorelease: snooze` mechanism.

   A proposal already running must finish before editing. Do not dispatch

   manual preparation over finalized notes.

2. On that release branch, save the reviewed inventory as

   `docs/releases/VERSION.contributions.json`. This is durable public release

   provenance, not a temporary planning file. Do not add credentials or local

   environment dumps. Keep the existing version artifacts aligned.

3. Run the existing checkpoint validator and the new checker:



   ```bash

   node scripts/release-notes.mjs check \

     --manifest docs/releases/VERSION.contributions.json

   node scripts/release-notes.mjs render \

     --manifest docs/releases/VERSION.contributions.json \

     --output /tmp/rea-VERSION.notes.md

   ```



   The checker supports inline PR bodies, including their surrounding metadata,

   up to GitHub's 65,536-character limit. It fails on larger notes rather than

   truncating credit; Release Please's overflow-link bodies are not integrated.



4. Update the release PR body with the rendered section while preserving its

   Release Please header/footer and component/version structure. Use a body

   file for `gh pr edit --body-file`; changing only `CHANGELOG.md` does not

   change Release Please's release body. Push only authorized changes.

5. Freshly fetch the PR body to a file and run `check --pr-body FILE`. Review

   the complete diff and wait for current CI. Publication checks the body

   again before release creation. Avoid further body edits while publishing.



The finalization label freezes bot refreshes, not main. New product changes

after the inventory target require refreshing the notes before publication.

The workflow checks target ancestry and allows only release metadata paths

after that target. It also requires the inventory target to equal the reviewed

merge's first parent, so intervening main commits require a fresh inventory.

Review diffs within the allowed release metadata paths too: the path guard does

not prove that package dependency/script edits are version-only changes.

To resume automatic proposals, remove the finalization label and let the bot

regenerate; expect editorial changes to be replaced.



Existing releases without a contribution inventory retain their current

publication path. Never retag or republish a package to correct release prose.





================================================================================

FILE: .agents/skills/rea-ci-tests-audit/SKILL.md

================================================================================



---

name: rea-ci-tests-audit

description: Audit REA CI and test suites for correctness, fixture drift, false passes, and measured performance; use for suite or workflow investigations and efficiency changes, rather than ordinary feature testing or a single test failure.

---



# REA CI and tests audit



Establish which checks still catch real regressions and which costs can be

removed without losing that protection. The outcome may be a verified fix,

an evidence-backed recommendation, or an explicit decision to stop.



Follow the checkout's `AGENTS.md`, \[suspicious link removed\],

and \[suspicious link removed\]. Use their current commands

and pinned toolchain, rather than commands remembered from an earlier audit.

Preserve the requested scope: investigation alone does not authorize edits;

this skill does not grant permission to publish issues, push, or merge. Existing

user authorization still applies. Keep audit notes and raw results outside the

tracked tree, normally in a task-specific `/tmp` directory.



## Establish the executed baseline



Fetch when the user asks for latest main. Pin the baseline SHA and inspected

workflow revision; use an isolated worktree when changing or comparing code.

Do not modify another task's checkout. Record dirty changes and the exact

command, toolchain, host, selected tests, instrumentation, and prerequisites.

An old run is evidence for its executed revision, even if main advances.



Trace workflow triggers, changed-path selection, job dependencies, reusable

actions, package scripts, test discovery, artifact producers, and report gates

through to the commands that actually execute. Include scripts, generated data,

runtime registration, and subprocess boundaries missing from import graphs.

Check positive and negative selection paths: required files must be discovered

once per intended test configuration; deliberate platform/configuration repeats

are separate coverage. A missing explicit test or missing required report must

not turn green. Optional lanes may skip; preserve their stated prerequisites.



Use existing timing and failure artifacts to select suspicious families. Run

relevant checks to establish a baseline; reserve a full local suite for broad

CI diagnosis or uncertainty that focused checks cannot resolve. Do not rebuild

or rerun an unchanged complete suite after every documentation edit.



## Prove the failure or protection



For each candidate, state the expected observable behavior and its owner,

then construct the smallest reproduction against production behavior. Follow

the producer and affected consumers before deciding where to fix it.



- For drift, compare fixtures with current admission requirements, protocol

  replies, named contracts, tool versions, and actual public entrypoints. A

  plausible-looking mock can fail before the behavior its test claims to cover.

  Search the whole affected fixture family, including other version strings.

  Preserve intentionally malformed fixtures and test their intended rejection.

- For a suspicious green test, perturb the relevant behavior in an isolated

  copy or inject a controlled failure. Verify that the existing assertion or

  gate detects it. A test may merely repeat its mock, import abandoned code,

  or hide a subprocess/checker failure. Restore mutations after the experiment.

- For shared setup or pruning, map distinct assertions to their retained

  scenarios. Preserve malformed inputs, cancellation, cleanup failure,

  permissions, capacity, identity, and meaningful concurrency interactions.

  A faster run that skips a case or weakens its oracle is not an improvement.

- For provider coverage, separate fake-producer, boundary, and actual-engine

  evidence. Inspect named skips and prerequisites; fixtures do not establish

  real Ghidra, LLDB, browser, or other provider behavior.



Classify findings as reproduced defects, supported costs, hypotheses, or

unavailable evidence. Record the baseline command, observed output/exit status,

expected result, affected scope, and competing explanation. A failure on main

may be pre-existing; that does not by itself make it irrelevant to a CI audit.

Attribute PR failures using the executed revision and a clean baseline, not

just their resemblance to a previous failure. Retry only to test a specific

transient explanation; retain the original failure and stop when repetition

adds no evidence. A passing retry does not establish a root cause or a fix.



## Assess efficiency without losing the gate



Read [measurement and CI checks](https://www.google.com/search?q=references/measurement-and-ci.md) when

investigating slowness, caching, runner waits, shared artifacts, or log noise.

Compare equivalent completed work before claiming a speedup. Distinguish

setup/build time, test execution, coverage instrumentation, dependency waits,

and runner scheduling; state which costs remain unmeasured.



Prefer removing proven duplicate preparation, reusing immutable setup, and

reducing repeated subprocess work before shrinking correctness coverage.

Preserve independent sessions where lifecycle or concurrency is the oracle.

Keep live tests fresh; a cached previous pass cannot validate current host,

installed provider contents, permissions, or external state.



## Fix, verify, and hand off within scope



If implementation is authorized, make the smallest structural change at the

owning boundary and add a regression that fails on the baseline for the right

reason. Retest affected consumers and meaningful negative paths; verify cache

invalidation or discovery when those mechanisms change. Read the installed

Turbo documentation before changing its configuration or commands.



Run the repository's applicable checks and inspect complete current-head CI

results before an authorized merge. Preserve required coverage and discovery

gates. Do not suppress a failure, add blanket retries, raise timeouts, or delete

distinct assertions solely to make CI green. Changes to these controls need

their own demonstrated reason and retained failure detection.



Report each confirmed issue with exact revision, reproduction, consequence,

proposed correction, and validation limits. Report performance with workload

and measurements, not just a percentage. Use English issue/PR records when

requested; follow the user's assignment, commit identity, review, and merge

preferences without assuming them for other users. Open ready-for-review PRs

only when that lifecycle is authorized. Resolve necessary review findings and

check final main against the tested tree after merging.



Stop when the authorized work is verified, remaining benefits are unproven,

or further changes would trade correctness for speculative speed. List genuine

uncertainties without turning them into additional optimization rounds.





================================================================================

FILE: .agents/skills/rea-ci-tests-audit/https://www.google.com/search?q=references/measurement-and-ci.md

================================================================================



# Measurement and CI checks



## Equivalent completed work



Record the source/workflow SHA, command, test identities and counts, skips,

assertions or output contract, exit status, coverage scope and thresholds,

toolchain/provider versions, host resources, and prepared artifacts. Inspect

both the child result and its report: a profiling wrapper may exit successfully

after the measured command failed. Focused tests can pass while global coverage

thresholds fail; describe both rather than calling the command green.



Measure wall time, user/system CPU, and peak process-family memory for relevant

completed tasks. Parent-only RSS misses workers and their children. On Linux,

summed RSS can double-count shared pages; report RSS/PSS semantics, sampling

interval, missing samples, and observed cleanup limits. Use equivalent host

tools elsewhere. State unknown costs, including agent tokens; fewer log bytes

alone prove neither fewer tokens nor faster tests.



Separate cold execution, warm build/file caches, and warm runtime caches.

Use repeated or alternating runs when variance affects the decision, with

enough observations to distinguish the proposed benefit from noise. Keep

workload, instrumentation, and host conditions comparable; record interference.

A run with fewer tests, early rejection, lost coverage, or a different runner

does not prove suite acceleration. CI-wide claims need end-to-end measurements,

not an extrapolation from one improved family.



## Workflow, caches, and shared artifacts



Trace each reused result from producer to consumers and identify its lifetime.

Check key/input coverage against the actual file inventory and result-affecting

configuration, environment, generated data, tool versions, and host state.

Exercise an affected input change to prove invalidation; exercise an irrelevant

change to support reuse where useful. Cache deterministic preparation and

static analysis only when their inputs fully describe the result.



Verify downloaded artifacts match the expected revision, platform, runtime,

and schema. Check restore misses, failed/partial producers, stale reports,

removed output files, and consumers after producer failures. Shared writers

need output ownership or locks; tests need isolated state, not an unnecessary

global lock. Worker counts do not bound children spawned within each test.

Preserve intentionally concurrent scenarios while bounding unrelated batches.



Check matrix expansion and all job pages before saying CI passed. Inspect

required gates after failed, cancelled, and skipped dependencies. `always()`

alone does not preserve failures; inspect the aggregation logic. Test/report

uploads should retain available diagnostics after failure, while absent or

malformed required results must fail closed. Do not demand an optional report

from a lane intentionally excluded by the selector.



## Runner waits and console noise



Use per-job and per-step timestamps where available. Workflow creation to job

start includes dependencies and other delays; it is not necessarily runner

queue time. Identify when the job became eligible before attributing waits to

runner capacity. If eligibility/queue timestamps are unavailable, report the

combined delay and unknown split. Compare equivalent lanes and runner types

across enough runs; a single busy runner is not a workflow regression.



For console reductions, retain checker exit codes, actionable errors, useful

summary counts, and complete machine-readable artifacts. Verify authored code

remains in the actual checker inventory when excluding generated outputs.

Introduce an authored error as a control; it must still fail. An ignore pattern

can hide real source as well as noise. Show that cached reports are restored,

stale successful reports cannot mask current failures, and report parse errors

remain failures. Measure readability or byte reduction separately from runtime.





================================================================================

FILE: .agents/skills/rea-ci-tests-audit/agents/openai.yaml

================================================================================



interface:

  display_name: "REA CI and tests audit"

  short_description: "Audit CI/test correctness and measured performance"

  default_prompt: "Use $rea-ci-tests-audit to investigate CI and test correctness, drift, and performance before proposing changes."





================================================================================

FILE: .agents/skills/rea-tool-design/SKILL.md

================================================================================



---

name: rea-tool-design

description: Design or change REA investigation tools, CLI/MCP contracts, provider capabilities, and Evidence semantics.

---



# REA tool design



Use the \[suspicious link removed\] for tool boundaries,

contract semantics, provider ownership, and discoverability. Inspect the current

contract and nearest existing tool relevant to the analyst question; source,

documentation, and live catalogs may describe different versions.



For a design request, return the proposed boundary, input/result shape, Evidence

semantics, nearest alternative, and verification approach. Implement when

requested, preserving the user's scope and existing authorization.



For implementation or verification, consult \[suspicious link removed\]

for the affected consumer and provider lanes, and

\[suspicious link removed\] for generated-file ownership. Read

provider/workflow guides only as the task requires.

