# Survey on Video and Multimodal Generation

## TL;DR
- Text-to-video (T2V) models are increasingly viewed as visual world models and are moving past early heuristic extraction methods [1][2].
- Multimodal Large Language Models (MLLMs) and any-to-any architectures are eliminating modality-specific pipelines by unifying text, image, audio, and video processing in shared latent flow spaces or autoregressive frameworks [3][4][5].
- Evaluation of video generation is evolving past single-value metrics to multi-dimensional benchmarks that assess physical realism, semantic alignment, and temporal consistency [6][7].
- A major persistent bottleneck in the field is the scarcity of high-quality long video datasets [8].

## Background
Historically, video generation and multimodal synthesis relied heavily on heuristic extraction, limited visual saliency techniques, or isolated generative pipelines [2]. The evolution of foundation models shifted the landscape, integrating large language models with early generative adversarial networks (GANs) and spatial diffusion models [9][4]. Early text-to-video capabilities typically involved extending text-to-image structures by adding a third temporal dimension (e.g., through 3D convolutions), which significantly raised computational requirements [9]. Today, replicating the dynamic physical world is viewed as a critical step toward Artificial General Intelligence, demanding unified architectures capable of rendering long, temporally coherent sequences across modalities [10].

## Text-to-Video and Diffusion Transformers
Recent breakthroughs in text-to-video models leverage Diffusion Transformer (DiT) architectures, combining the iterative noise-reduction of diffusion models with the scalability of transformers [1]. This approach generates higher-quality, structurally coherent videos, establishing models like OpenAI's Sora, Google's Veo 3, and Runway's Gen-4.5 as powerful visual world models [1]. OpenAI's Sora utilizes prompt "recaptioning" via GPT models to enforce tighter semantic alignment [11]. Furthermore, open-source implementations such as CogVideoX, HunyuanVideo, and Open-Sora Plan are rapidly matching proprietary benchmarks in high-resolution, long-duration synthesis [1][11][12]. However, managing the quadratic memory demands of joint 3D spatiotemporal attention remains difficult; researchers are currently deploying sparse attention, autoregressive variants, and 3D VAE token compression to optimize efficiency [11][12].

## Any-to-Any Multimodal Frameworks
Multimodal generative research is migrating from modality-specific pipelines toward unified any-to-any generation systems [5][10]. Approaches can be broadly categorized into autoregressive architectures and continuous flow-based models. Autoregressive models like AR-Omni support multimodal input and output generation using a single Transformer decoder [3]. Conversely, latent variable and flow models such as OmniFlow and MUNITE unify inference by modeling a shared conditional flow or latent space over multiple modalities, allowing generative paths between arbitrary subsets of data types [13][5]. Jointly modeling audio and vision is essential in modern large foundation models (e.g., Meta MovieGen) for reasoning across dynamic, temporally grounded signals [14]. 

## Evaluation Metrics and Open Problems
Assessing generated video quality has proven exceptionally challenging. Conventional frame-level metrics such as Fréchet Inception Distance (FID) and video-level indicators like Fréchet Video Distance (FVD) fail to fully capture semantic naturalness or text alignment [7][8]. Consequently, modern evaluations rely on multi-dimensional benchmarks like VBench, which separately measure visual fidelity, temporal consistency, semantic alignment, and physical coherence [6]. 

## Trends and open problems
A significant problem is that current models face challenges maintaining physical realism [6][10]. Furthermore, the lack of large-scale, high-quality long video datasets hampers the optimal training of models [8]. Over extended durations, generated videos are still susceptible to frame skipping, abrupt scene transitions, motion incoherence, and error accumulation [6][8]. Finally, the trade-off between maintaining computational efficiency and achieving complex physical simulations across modalities will likely dictate the immediate future of multimodal generative AI research [11][3][10].

## References
[1] Sora as a World Model? A Complete Survey on Text-to-Video Generation. web. https://arxiv.org/html/2403.05131v3 (unknown)
[2] Generative AI for Video Trailer Synthesis: From Extractive Heuristics to Autoregressive Creativity. arxiv. https://arxiv.org/abs/2604.04953 (2026-04-03)
[3] AR-Omni: A Unified Autoregressive Model for Any-to-Any Generation. hf-search. https://huggingface.co/papers/2601.17761 (2026-01-25)
[4] NExT-GPT: Any-to-Any Multimodal LLM. hf-search. https://huggingface.co/papers/2309.05519 (2023-09-11)
[5] MUNITE: Unified Multimodal Latent Inference for Any-to-Any Multimodal Generation. arxiv. https://arxiv.org/abs/2610.09866 (2026-10-07)
[6] Generative AI Video Evaluation: Survey of Metrics, Benchmarks, and Trustworthiness. web. https://openaccess.thecvf.com/content/CVPR2026W/VGBE/papers/Safavigerdini_Generative_AI_Video_Evaluation_Survey_of_Metrics_Benchmarks_and_Trustworthiness_CVPRW_2026_paper.pdf (unknown)
[7] Measuring the Quality of Text-to-Video Model Outputs: Metrics and Dataset. web. https://www.deep.ai/publication/measuring-the-quality-of-text-to-video-model-outputs-metrics-and-dataset (2023-09-14)
[8] A Survey on Long Video Generation: Challenges, Methods .... web. https://arxiv.org/html/2403.16407v1 (unknown)
[9] Video Diffusion Models: A Survey. web. https://arxiv.org/abs/2405.03150 (2024-11-17)
[10] Simulating the Real World: A Unified Survey of Multimodal Generative Models. arxiv. https://arxiv.org/abs/2503.04641 (2025-03-06)
[11] Generative AI for Text-to-Video Generation: Recent Advances. web. https://www.mdpi.com/2673-6470/6/1/23 (2026-03-09)
[12] Open-Sora Plan: Open-Source Large Video Generation Model. hf-daily. https://huggingface.co/papers/2412.00131 (2024-11-28)
[13] OmniFlow: Any-to-Any Generation with Multi-Modal Rectified Flows. hf-search. https://huggingface.co/papers/2412.01169 (2024-12-02)
[14] Audio-Visual Intelligence in Large Foundation Models. arxiv. https://arxiv.org/abs/2605.04045 (2026-05-05)
