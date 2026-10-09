# A Survey of Reinforcement Learning for LLM Reasoning

## TL;DR
- Foundational RL methods like PPO are being optimized for LLMs through critic-free architectures (e.g., GRPO) and token-level advantage policies to reduce overhead and improve multi-step logic stability [1].
- Outcome-only reinforcement learning and Reasoning State Propagation allow the induction of Process Reward Models (PRMs) without relying on expensive human step annotation [2][3].
- Tree search methods combined with process reward guidance, such as ReST-MCTS*, bypass manual annotation and enhance training trace quality over Best-of-N approaches [4].
- Advanced frameworks are utilizing dual-role self-play architectures (Proposer/Solver) to continuously scale task difficulty without relying on curated datasets [5][6].

## Background
Reinforcement Learning (RL) has become a primary driver in enhancing the reasoning capabilities of Large Language Models (LLMs). Early alignment efforts relied heavily on Reinforcement Learning from Human Feedback (RLHF) to optimize behavior [7]. However, reasoning tasks pose unique challenges, particularly the issue of sparse rewards in multi-step logic and the training instability of Actor-Critic (AC) methods [8]. Traditional Proximal Policy Optimization (PPO) infers intermediate step contributions but suffers from credit assignment bias and significant memory overhead [9][1]. To solve this, recent research focuses on specialized policy optimization, nuanced reward modeling, and autonomous self-evolution through synthetic data.

## Foundational RL Methods Adapted for Reasoning
The need for stable and efficient training has spurred adaptations of foundational RL techniques for LLMs. PPO utilizes an actor-critic model, which can be unstable for complex reasoning tasks [1]. To address this, Group Relative Policy Optimization (GRPO) removes the critic model and calculates relative advantages within a local batch of responses [1]. Further advancements like Direct Advantage Policy Optimization (DAPO) transition from sample-level to token-level policy gradient loss to promote detailed reasoning chains and prevent models from gaming the system with short answers [1].

In contrast, Direct Preference Optimization (DPO) simplifies optimization by leveraging preference data without an explicit reward model [9]. Alternatives like REINFORCE++ optimize for verifiable outcomes while using stringent format rewards to prevent reasoning shortcuts, achieving higher stability and training efficiency than standard PPO and GRPO [10].

## Process vs. Outcome Reward Modeling
Effectively assigning rewards to intermediate steps is critical for multi-step reasoning. Process Reward Models (PRMs) assess these steps but usually require costly human annotation or computationally heavy Monte Carlo estimation, which can perform poorly if completion models are unreliable [11]. Furthermore, Best-of-N evaluation strategies optimized for PRMs can exhibit bias by favoring outcome-based assessment over process-based quality [11].

Recent efforts aim to bypass this manual annotation cost. The TIPS framework uses outcome-only reinforcement learning, reinforcing step-level verification via group-relative advantage based on the final outcome, bypassing explicit process supervision [2]. Similarly, Reasoning State Propagation (RSP) models reasoning prefixes with binary validity states, allowing final outcome labels to supervise intermediate step transitions [3].

## Tree Search and MCTS Integration
To elevate the quality of reasoning traces for self-training, researchers are combining PRMs with search algorithms. Traditional Best-of-N or Tree-of-Thought approaches are being surpassed by methods like ReST-MCTS* [4]. ReST-MCTS* integrates process reward guidance with Monte Carlo Tree Search, estimating the probability that a step leads to a correct answer given oracle outcomes. This approach successfully refines process reward models and generates high-quality traces for policy self-training without manual per-step annotations [4].

## Self-Play and Synthetic Auto-Curricula
A significant breakthrough in scaling reasoning capabilities is the use of self-play and synthetic data generation, mitigating the dependence on finite human datasets. Frameworks like SeRL utilize self-rewarding modules with majority-voting to bootstrap LLM reasoning on limited data [12].

To avoid the plateauing effect (mode collapse) of standard self-play loops, systems adopt multi-agent or dual-role formulations. Research indicates that systems need asymmetric co-evolution between a Proposer (task generation) and a Solver (attempting solutions) [13]. In the OPT-Zero framework, an LLM Proposer generates increasingly challenging optimization problems that directly enhance the Solver's capabilities via verifiable ground truth from external solvers [5]. Similarly, the LURE framework casts zero-data self-play as a pursuit-evasion game, automatically positioning tasks at optimal difficulties via a capture-frontier reward [6]. Furthermore, the SynCo framework couples a Synthesizer and Reasoner in multi-agent RL, where tasks dynamically adapt to the Reasoner's evolving capability state, preventing stagnation [14].

## Trends and open problems
The trajectory of RL in LLM reasoning points toward entirely self-sustaining, zero-data self-evolution pipelines. However, several open problems remain. Credit assignment for ultra-long reasoning trajectories is still imperfect. Additionally, ensuring that auto-generated tasks do not anchor capabilities to narrow domains (Capability Anchoring) requires proactive external information seeking and careful asymmetric co-evolution design [13][5]. As models rely more heavily on synthetic supervision, maintaining the robustness of automated verifiers against "reward hacking" in highly complex reasoning environments remains a critical research frontier.

## References
[1] Comparative Analysis and Parametric Tuning of PPO, GRPO, and DAPO for LLM Reasoning Enhancement. web. https://arxiv.org/html/2512.07611v1 (unknown)
[2] Inducing Process Supervision from Outcome-Only Reinforcement Learning. arxiv. https://arxiv.org/abs/2609.36641 (2026-09-29)
[3] Learning Process Rewards via Reasoning State Propagation. arxiv. https://arxiv.org/abs/2609.39220 (2026-09-30)
[4] ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search. hf-search. https://huggingface.co/papers/2406.03816 (2024-06-06)
[5] Self-Evolving LLMs: Sustainable Data Pipelines. web. https://www.arxiv.org/pdf/2603.02218 (unknown)
[6] Learning to Optimize through Solver-Grounded Self-Play. arxiv. https://arxiv.org/abs/2609.34205 (2026-09-28)
[7] A Technical Survey of Reinforcement Learning Techniques for Large Language Models. arxiv. https://arxiv.org/abs/2507.04136 (2025-07-05)
[8] Improving Multi-Step Reasoning Abilities of Large Language Models with Direct Advantage Policy Optimization. arxiv. https://arxiv.org/abs/2412.18279 (2024-12-24)
[9] Towards Large Reasoning Models: A Survey of Reinforced Learning for LLM Reasoning. web. https://arxiv.org/abs/2501.09686 (unknown)
[10] Logic-RL: Unleashing LLM Reasoning with Rule-Based Reinforcement Learning. web. https://arxiv.org/abs/2502.14768 (2025-02-20)
[11] The Lessons of Developing Process Reward Models in Mathematical Reasoning. hf-search. https://huggingface.co/papers/2501.07301 (2025-01-13)
[12] SeRL: Self-Play Reinforcement Learning for Large Language Models with Limited Data. web. https://proceedings.neurips.cc/paper_files/paper/2025/file/95c2cbe23fb6d28a4ae908aa7f3de5bf-Paper-Conference.pdf (unknown)
[13] Synthetic Data Generation & Multi-Step RL for Reasoning. web. https://scalingintelligence.stanford.edu/pubs/sdgrl/ (unknown)
[14] SynCo: Data Synthesis Co-Training for Self-Evolving LLMs via Multi-Agent Reinforcement Learning. web. https://arxiv.org/html/2610.11345 (unknown)
