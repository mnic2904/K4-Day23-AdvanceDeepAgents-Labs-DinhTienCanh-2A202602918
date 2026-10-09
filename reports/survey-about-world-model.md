# Survey about World Models

## TL;DR
- Various methods for creating world models encompass video generation and autonomous systems [1][2][3].
- World models enhance decision-making capabilities across various applications, significantly in robotics and autonomous driving [4][5].
- Major challenges include generalization across environments and the need for unified, reproducible evaluation frameworks [6][7].

## Background
World models learn compact representations of an environment and use them to predict future states, enabling policies to be trained through imagined interactions rather than only direct experience [3]. This capability is important in robotics and other sequential decision-making settings where real-world interaction is costly.

## Approaches for Creating World Models
The foundational **World Models** approach combines a compact latent representation with a learned dynamics model so an agent can train a controller inside its predicted environment [3]. More recent video-centric systems scale this idea differently: **WorldDreamer** predicts masked visual tokens for general video modeling [1], while **iVideoGPT** jointly represents observations, actions, and rewards with an autoregressive transformer for interactive environments [2]. Together, these approaches show a shift from compact task-specific simulators toward higher-capacity generative models, while retaining the core goal of predicting how environments evolve.

## Importance and Applications of World Models in Machine Learning
World models are increasingly connected to embodied control. **VioLA** learns generalist humanoid control policies from human data, illustrating how predictive representations can support complex physical behavior [4]. A broader survey organizes world-model research around the tension between learning useful internal understanding and predicting future observations, and reviews applications including robotics and autonomous driving [5]. These uses differ in output—control actions versus predicted futures—but both depend on representations that remain reliable outside the training distribution.

## Trends and open problems
Significant challenges still exist in developing effective world models. Critical issues include:
- Framework fragmentation and the need for integrative approaches to model interaction, perception, and reasoning [6]. 
- The existence of a sim-to-real gap, particularly in cases where environments are high-dimensional, complicates the practicality and efficiency of world models [7]. 
- Evaluation remains difficult because predictive accuracy alone does not guarantee that a learned representation contains the causal or controllable structure needed by an agent [5][6].

The future of world models lies in refining these frameworks to enhance robustness, adaptability, and real-world applicability.

## References
[1] WorldDreamer: Towards General World Models for Video Generation via Predicting Masked Tokens. hf-search. https://huggingface.co/papers/2401.09985 (2024-01-18)
[2] iVideoGPT: Interactive VideoGPTs are Scalable World Models. hf-search. https://huggingface.co/papers/2405.15223 (2024-05-24)
[3] World Models. hf-search. https://huggingface.co/papers/1803.10122 (2018-03-27)
[4] VioLA: Learning Generalist Humanoid Control Policies from Human Data. arxiv. https://arxiv.org/abs/2610.12435 (2026-10-08)
[5] Understanding World or Predicting Future? A Comprehensive Survey of World Models. web. https://dl.acm.org/doi/10.1145/3746449 (2025-09-09)
[6] Stable-worldmodel-v1: Reproducible World Modeling Research and Evaluation. hf-search. https://huggingface.co/papers/2602.08968 (2026-02-09)
[7] Research on World Models Is Not Merely Injecting World Knowledge into Specific Tasks. hf-search. https://huggingface.co/papers/2602.01630 (2026-02-02)
