# A Survey of Reinforcement Learning for LLM Reasoning

## TL;DR
- Foundational RL methods like PPO are being optimized for LLMs through critic-free architectures (e.g., GRPO) and token-level advantage policies to reduce overhead and improve multi-step logic stability [4].
- Outcome-only reinforcement learning and Reasoning State Propagation allow the induction of Process Reward Models (PRMs) without relying on expensive human step annotation [6, 9].
- Tree search methods combined with process reward guidance, such as ReST-MCTS*, bypass manual annotation and enhance training trace quality over Best-of-N approaches [8].
- Advanced frameworks are utilizing dual-role self-play architectures (Proposer/Solver) to continuously scale task difficulty without relying on curated datasets [13, 14].

## Background
Reinforcement Learning (RL) has become a primary driver in enhancing the reasoning capabilities of Large Language Models (LLMs). Early alignment efforts relied heavily on Reinforcement Learning from Human Feedback (RLHF) to optimize behavior [1]. However, reasoning tasks pose unique challenges, particularly the issue of sparse rewards in multi-step logic and the training instability of Actor-Critic (AC) methods [2]. Traditional Proximal Policy Optimization (PPO) infers intermediate step contributions but suffers from credit assignment bias and significant memory overhead [3, 4]. To solve this, recent research focuses on specialized policy optimization, nuanced reward modeling, and autonomous self-evolution through synthetic data.

## Foundational RL Methods Adapted for Reasoning
The need for stable and efficient training has spurred adaptations of foundational RL techniques for LLMs. PPO utilizes an actor-critic model, which can be unstable for complex reasoning tasks [4]. To address this, Group Relative Policy Optimization (GRPO) removes the critic model and calculates relative advantages within a local batch of responses [4]. Further advancements like Direct Advantage Policy Optimization (DAPO) transition from sample-level to token-level policy gradient loss to promote detailed reasoning chains and prevent models from gaming the system with short answers [4]. 

In contrast, Direct Preference Optimization (DPO) simplifies optimization by leveraging preference data without an explicit reward model [3]. Alternatives like REINFORCE++ optimize for verifiable outcomes while using stringent format rewards to prevent reasoning shortcuts, achieving higher stability and training efficiency than standard PPO and GRPO [5].

## Process vs. Outcome Reward Modeling
Effectively assigning rewards to intermediate steps is critical for multi-step reasoning. Process Reward Models (PRMs) assess these steps but usually require costly human annotation or computationally heavy Monte Carlo estimation, which can perform poorly if completion models are unreliable [7]. Furthermore, Best-of-N evaluation strategies optimized for PRMs can exhibit bias by favoring outcome-based assessment over process-based quality [7]. 

Recent efforts aim to bypass this manual annotation cost. The TIPS framework uses outcome-only reinforcement learning, reinforcing step-level verification via group-relative advantage based on the final outcome, bypassing explicit process supervision [6]. Similarly, Reasoning State Propagation (RSP) models reasoning prefixes with binary validity states, allowing final outcome labels to supervise intermediate step transitions [9]. 

## Tree Search and MCTS Integration
To elevate the quality of reasoning traces for self-training, researchers are combining PRMs with search algorithms. Traditional Best-of-N or Tree-of-Thought approaches are being surpassed by methods like ReST-MCTS* [8]. ReST-MCTS* integrates process reward guidance with Monte Carlo Tree Search, estimating the probability that a step leads to a correct answer given oracle outcomes. This approach successfully refines process reward models and generates high-quality traces for policy self-training without manual per-step annotations [8].

## Self-Play and Synthetic Auto-Curricula
A significant breakthrough in scaling reasoning capabilities is the use of self-play and synthetic data generation, mitigating the dependence on finite human datasets. Frameworks like SeRL utilize self-rewarding modules with majority-voting to bootstrap LLM reasoning on limited data [10]. 

To avoid the plateauing effect (mode collapse) of standard self-play loops, systems adopt multi-agent or dual-role formulations. Research indicates that systems need asymmetric co-evolution between a Proposer (task generation) and a Solver (attempting solutions) [12]. In the OPT-Zero framework, an LLM Proposer generates increasingly challenging optimization problems that directly enhance the Solver's capabilities via verifiable ground truth from external solvers [13]. Similarly, the LURE framework casts zero-data self-play as a pursuit-evasion game, automatically positioning tasks at optimal difficulties via a capture-frontier reward [14]. Furthermore, the SynCo framework couples a Synthesizer and Reasoner in multi-agent RL, where tasks dynamically adapt to the Reasoner's evolving capability state, preventing stagnation [11].

## Trends and open problems
The trajectory of RL in LLM reasoning points toward entirely self-sustaining, zero-data self-evolution pipelines. However, several open problems remain. Credit assignment for ultra-long reasoning trajectories is still imperfect. Additionally, ensuring that auto-generated tasks do not anchor capabilities to narrow domains (Capability Anchoring) requires proactive external information seeking and careful asymmetric co-evolution design [12, 13]. As models rely more heavily on synthetic supervision, maintaining the robustness of automated verifiers against "reward hacking" in highly complex reasoning environments remains a critical research frontier.

## References

[1] A Technical Survey of Reinforcement Learning Techniques for Large Language Models. arxiv. https://arxiv.org/abs/2507.04136 (2025-07-05)
[2] Improving Multi-Step Reasoning Abilities of Large Language Models with Direct Advantage Policy Optimization. arxiv. https://arxiv.org/abs/2412.18279 (2024-12-24)
[3] Towards Large Reasoning Models: A Survey of Reinforced Learning for LLM Reasoning. arxiv. https://arxiv.org/abs/2501.09686 (unknown)
[4] Comparative Analysis and Parametric Tuning of PPO, GRPO, and DAPO for LLM Reasoning Enhancement. web. https://arxiv.org/html/2512.07611v1 (unknown)
[5] Logic-RL: Unleashing LLM Reasoning with Rule-Based Reinforcement Learning. arxiv. https://arxiv.org/abs/2502.14768 (2025-02-20)
[6] Inducing Process Supervision from Outcome-Only Reinforcement Learning. arxiv. https://arxiv.org/abs/2609.36641 (2026-09-29)
[7] The Lessons of Developing Process Reward Models in Mathematical Reasoning. hf-search. https://huggingface.co/papers/2501.07301 (2025-01-13)
[8] ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search. hf-search. https://huggingface.co/papers/2406.03816 (2024-06-06)
[9] Learning Process Rewards via Reasoning State Propagation. arxiv. https://arxiv.org/abs/2609.39220 (2026-09-30)
[10] SeRL: Self-Play Reinforcement Learning for Large Language Models with Limited Data. web. https://proceedings.neurips.cc/paper_files/paper/2025/file/95c2cbe23fb6d28a4ae908aa7f3de5bf-Paper-Conference.pdf (unknown)
[11] SynCo: Data Synthesis Co-Training for Self-Evolving LLMs via Multi-Agent Reinforcement Learning. web. https://arxiv.org/html/2610.11345 (unknown)
[12] Synthetic Data Generation & Multi-Step RL for Reasoning. web. https://scalingintelligence.stanford.edu/pubs/sdgrl/ (unknown)
[13] Self-Evolving LLMs: Sustainable Data Pipelines. web. https://www.arxiv.org/pdf/2603.02218 (unknown)
[14] Learning to Optimize through Solver-Grounded Self-Play. arxiv. https://arxiv.org/abs/2609.34205 (2026-09-28)
