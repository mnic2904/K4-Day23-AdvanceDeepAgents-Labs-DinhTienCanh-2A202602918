# Survey on LLM Agents and Tool Use

## TL;DR
- Large Language Model (LLM) agents are evolving from static text generators into autonomous systems capable of executing complex, long-horizon tasks across web and software environments by leveraging tools [1].
- Architectural paradigms such as ReAct and Reflexion have pioneered explicit reasoning traces and self-correction, while multi-plan approaches like Tree of Thoughts integrate classical search algorithms to improve planning [2][3][4].
- Tool integration has advanced from self-supervised learning methods (Toolformer) to sophisticated retrieval-augmented systems (Gorilla) and methods that decouple reasoning chains from tool execution to enable parallel operations [5][6][7].
- Key challenges restricting real-world deployment include the propagation of hallucinations in multi-agent settings, fragile evaluation frameworks, and critical security and safety concerns such as tool misuse [1][8][9].

## Background
The rapid progression of Large Language Models has sparked a transition towards agentic AI. Instead of acting merely as reactive chatbots, these LLMs serve as the cognitive core of autonomous agents designed to perceive environments, plan sequences of actions, and manipulate external tools to achieve complex goals [1][10]. The capability to interface with external APIs, search engines, and physical systems shifts the paradigm from pure text synthesis to interactive problem solving. This survey examines the architectural foundations that enable agentic reasoning, the methods by which models learn and manage tool use, the evaluation of these systems, and the open challenges facing their real-world integration.

## Agent Architectures and Planning Capabilities
A core differentiator of an LLM agent is its ability to reason and plan. This capability has been widely categorized into several distinct paradigms:

- **Task Decomposition and Sequential Planning:** Models prompt step-by-step thinking to break down complex tasks. The foundational ReAct framework advances this by explicitly forcing the agent to alternate between generating reasoning traces ("Thoughts") and executing external actions, allowing continuous state tracking [2][3].
- **Multi-plan Exploration:** Rather than greedy sequential execution, frameworks like Tree of Thoughts (ToT) treat planning as a search problem over a tree of reasoning steps [4]. By utilizing breadth-first or depth-first search combined with backtracking, the agent explores multiple reasoning paths before committing to an action [4].
- **Reflection and Refinement:** Iterative self-improvement loops have become critical. The Reflexion framework extends ReAct by utilizing an evaluator model to score outputs and a reflector model to generate verbal reinforcement cues [2][4]. When actions fail, the agent creates a reflection that is stored in episodic memory, which refines subsequent planning attempts [2][3].

Current agent architectures are increasingly described as "neurosymbolic", blending deep learning representations with symbolic AI traditions like classic reasoning and external search [4].

## Tool Learning and Integration Strategies
To interact with the outside world, LLMs must learn to efficiently call and integrate external tools.

- **Self-Supervised and Finetuned Tool Use:** Early breakthroughs like Toolformer demonstrated that LLMs could self-supervisedly teach themselves to use tools via simple APIs, learning to decide which APIs to call and how to incorporate the results into token prediction using just a few demonstrations [6]. Models like Gorilla, a finetuned LLaMA, push this further by integrating a document retriever, enabling the model to adapt to frequent API updates and significantly mitigating hallucinations during API calls [7].
- **Abstract Reasoning Chains:** Techniques like the Chain-of-Abstraction (CoA) method train LLMs to decode reasoning chains containing abstract placeholders. Specific knowledge is then filled by calling domain tools, which enables the model to perform decoding and external tool calling in parallel rather than suffering inference delays waiting for tool responses [5].
- **Tool Selection and Awareness:** As toolsets scale, the challenge shifts from basic invocation to tool selection. The MetaTool benchmark highlights that many LLMs struggle with "tool awareness"—deciding whether to use a tool at all—and selecting the appropriate tool from a vast collection, indicating a remaining gap between LLMs and genuine intelligent agents [11]. Detailed tool descriptions have been shown to be essential for improving tool selection performance [11].

## Applications and Multi-Agent Systems
The practical applications of LLM agents have rapidly expanded. They are deployed in software and systems automation, data science lifecycle management, and complex orchestrations like autonomous driving and AI hospitals [12]. 

A major trend is the development of Task-Oriented Multi-Agent Systems (LLM-MAS), where frameworks structure multiple agents to coordinate, debate, or simulate complex organizational dynamics [1][8]. Furthermore, these agents are transitioning from merely using existing tools to "tool-making"—synthesizing new APIs that can be reused by themselves or other agents to solve interactive tasks [1]. To manage integration fragmentation, the field is moving toward standardized interoperability protocols, such as the Model Context Protocol (MCP), decoupling agents from bespoke tool implementations [12][13].

## Trends and open problems
Despite rapid advancements, several critical challenges remain unresolved:
- **Cascading Hallucinations and Tool Misuse:** In multi-agent systems, a hallucination or error from one agent can rapidly propagate through the network [8]. Tool misuse, such as hallucinated API calls or misinterpreting tool outputs, leads to fragile grounding and error accumulation over long trajectories [1].
- **Context Management in Long-Horizon Tasks:** Over extended tasks, pure textual summaries often exhaust the context window or lose fidelity. Emerging solutions include learning residual soft memory tokens (REMORY) to supplement text summaries for context compaction [14].
- **Evaluation Deficiencies:** Benchmarks have historically focused on isolated function-calling correctness. However, systems like ACEBench are pushing evaluation toward end-to-end task completion in complex, multi-turn, and ambiguous scenarios [15][13]. The broader field of LLM agent evaluation still lacks systematic frameworks, especially concerning dynamic environments and enterprise compliance constraints [9].
- **Safety, Governance, and Scalability:** High autonomy combined with tool execution raises severe security risks, including privacy leaks, IP exploitation, and backdoor vulnerabilities [12]. As agent networks scale, "Agent Orchestration"—including workflow optimization and limiting redundant communication—becomes a significant bottleneck, and clear multi-agent scaling laws remain elusive [8].

## References
[1] From Language Models to Agentic AI: A Survey of Autonomous, Action-Enabled, and Collaborative LLM Agents. web. https://link.springer.com/article/10.1007/s12559-026-10619-1 (2026-08-24)
[2] Understanding the planning of LLM agents: A survey. web. https://arxiv.org/abs/2402.02716 (2024-02-05)
[3] LLM-based Agentic Reasoning Frameworks: A Survey from Methods to Scenarios. web. https://arxiv.org/html/2508.17692 (unknown)
[4] Agentic Large Language Models, a survey. web. https://arxiv.org/html/2503.23037v2 (2025-04-03)
[5] Efficient Tool Use with Chain-of-Abstraction Reasoning. arxiv. https://arxiv.org/abs/2401.17464 (2024-01-30)
[6] Toolformer: Language Models Can Teach Themselves to Use Tools. hf-search. https://huggingface.co/papers/2302.04761 (2023-02-09)
[7] Gorilla: Large Language Model Connected with Massive APIs. hf-search. https://huggingface.co/papers/2305.15334 (2023-05-24)
[8] Large Language Model based Multi-Agents: A Survey of Progress and Challenges. web. https://arxiv.org/html/2402.01680 (unknown)
[9] Evaluation and Benchmarking of LLM Agents: A Survey. hf-search. https://huggingface.co/papers/2507.21504 (2025-07-29)
[10] Forms of LLM-Integrated Applications from LLM-Chats to Autonomous AI Agent System. arxiv. https://arxiv.org/abs/2610.11899 (2026-10-08)
[11] MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use. hf-search. https://huggingface.co/papers/2310.03128 (2023-10-04)
[12] Large Language Model Agent: A Survey on Methodology, Applications and Challenges. web. http://arxiv.org/abs/2503.21460 (unknown)
[13] Agentic Tool Use in Large Language Models: A Survey. web. https://arxiv.org/html/2604.00835 (2026-06-29)
[14] REMORY: Learning Residual Memory for Context Compaction. hf-daily. https://huggingface.co/papers/2610.11287 (2026-10-08)
[15] ACEBench: Who Wins the Match Point in Tool Usage?. hf-search. https://huggingface.co/papers/2501.12851 (2025-01-22)
