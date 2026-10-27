<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header_dark.svg">
  <img src="assets/header_light.svg" width="100%" alt="Yann Klees. Data scientist. MSc Applied Data Science, Utrecht University. Based in Luxembourg.">
</picture>

<br>

<a href="https://github.com/YannKleees?tab=repositories">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/repo_map_dark.svg">
    <img src="assets/repo_map_light.svg" width="100%" alt="Map of my public projects. Each dot is a repository, placed by a PCA of the tools and topics it uses and sized by my commits. Click to open the repositories tab.">
  </picture>
</a>

### Featured

<details>
<summary><b>hyperreimpute</b>: reproduction of HyperImpute (ICML 2022). A tuned single CatBoost had 6 to 31% lower RMSE than HyperImpute on all 3 datasets.</summary>

<br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hyperreimpute_dark.svg">
  <img src="assets/hyperreimpute_light.svg" width="600" alt="Dot plot of imputation RMSE on the airfoil, compression and wine_white datasets. ICE with a tuned CatBoost has the lowest error on all three, below HyperImpute and the paper's column-naive baseline.">
</picture>

I reproduced Table 2 of the HyperImpute paper on three UCI datasets with 10 seeds each, reran the key methods under the older hyperimpute 0.1.5, and tested the method's limits under MCAR, MAR and MNAR missingness and on tables with few features. The paper's gain over the best single learner did not reproduce: the CatBoost learner in hyperimpute 0.1.17 defaults to 10 trees, and with sensible settings a single CatBoost beats the full method.

Stack: Python, hyperimpute and its CatBoost learners, pandas, NumPy, SciPy, seaborn.

[Repository](https://github.com/YannKleees/hyperreimpute)

</details>

### Toolbox

<!-- toolbox:start -->
<img src="https://skillicons.dev/icons?i=py,js,html,tensorflow&perline=12" height="40" alt="Python, JavaScript, HTML, TensorFlow">

Data and visualisation: pandas, NumPy, SciPy, Matplotlib, seaborn, NetworkX.
<!-- toolbox:end -->

### Contact

[LinkedIn](https://www.linkedin.com/in/yann-klees-a0b8a6334) · [yannklees@gmail.com](mailto:yannklees@gmail.com)
