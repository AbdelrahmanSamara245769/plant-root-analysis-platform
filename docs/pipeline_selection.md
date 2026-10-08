# Pipeline Selection

## Comparison table

All five team members' Block B pipelines were compared on the following criteria:

| Metric | Pipeline A | Pipeline B | Pipeline C | Pipeline D | Pipeline E |
|--------|--------|--------|--------|--------|--------|
| F1-score | 0.88 | 0.8201 | 0.8308 | 0.85 | N/A |
| sMAPE | 5.747 | 5.773 | 6.877 | 9.359 | 14.564 |
| Kaggle rank | 5 | 6 | 12 | 20 | 39 |
| Library | TensorFlow | TensorFlow | TensorFlow | TensorFlow | N/A |
| Model type | binary U-Net | binary U-Net | multiclass U-Net | binary U-Net | N/A |
| Model size | 104 MB | 355 MB | 31 MB | 22.4 MB | N/A |
| Weights size | 33 MB | 118 MB | 1 KB* | 7.40 MB | N/A |
| Code quality | .ipynb | .py files | one big .py file | .ipynb | N/A |

**Notes:**
- Pipeline E was incomplete and could not be evaluated on most criteria.
- Pipeline C uses a multiclass U-Net (root, shoot, seed, background) rather than binary classification. While not a dealbreaker, this adds complexity — retraining requires multi-class labeled data and additional evaluation metrics per class. Combined with its lower F1 score (0.83 vs 0.88), it was not selected.
- Pipeline A's sMAPE score (5.747) is from an earlier version of the model. The original model was lost during server maintenance and retrained. The F1 score of 0.88 is from the retrained model, which was not resubmitted to the Kaggle competition.

## Decision

**Selected pipeline: A**

**Reasoning:**
- Highest F1 score (0.88) across all candidates
- Kaggle rank 5th (best in team)
- Reasonable model size (104 MB model, 33 MB weights) — lighter than pipeline B (355 MB)
- All team members use TensorFlow, so no framework conflict regardless of choice
- Full end-to-end pipeline from raw image to root tip coordinates with mm conversion
- While pipeline B had the advantage of already being in .py files, refactoring notebooks into modules was planned work anyway and spreads the coding effort across the team

**Selected model details:**
- Architecture: Attention U-Net (binary classification)
- Framework: TensorFlow/Keras
- Input: 256×256 grayscale patches (single channel)
- Parameters: ~8.9M
- Weights file: unet_256px.h5
- Custom metric: F1 score
