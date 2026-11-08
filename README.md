<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header_dark.svg">
  <img src="assets/header_light.svg" width="100%" alt="Yann Klees, data science student from Luxembourg. MSc Applied Data Science at Utrecht University, BSc Data Science and AI at Maastricht University. Works on NLP, computer vision and recommender systems. Speaks Luxembourgish, English, French and German.">
</picture>

<details open>
<summary><b><code>~/projects</code></b> &nbsp;click a folder to open it</summary>
<br>
<blockquote>

<details>
<summary><b><code>nlp-and-privacy/</code></b> &nbsp;2 projects</summary>
<blockquote>

<details>
<summary><code>tagging/</code> &nbsp;finds and redacts personal data in Luxembourgish, French, German and English text</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/tagging">tagging/</a>
├── <a href="https://github.com/YannKleees/tagging/tree/main/core">core/</a>        Rust engine: rules and gazetteers
├── <a href="https://github.com/YannKleees/tagging/tree/main/tagging">tagging/</a>     Python side: GLiNER model, merging, post-processing
├── <a href="https://github.com/YannKleees/tagging/tree/main/eval">eval/</a>        datasets, benchmark and evaluation
├── <a href="https://github.com/YannKleees/tagging/tree/main/tests">tests/</a>
└── <a href="https://github.com/YannKleees/tagging#readme">README.md</a>
</pre>

Recall on hard Luxembourgish names rises from 0.57 with rules alone to 0.91 with the model added, at precision 1.00.
<br><sub>Rust · Python · GLiNER</sub> &nbsp; **[open repo →](https://github.com/YannKleees/tagging)**

</details>

<details>
<summary><code>pii-anonymisation-thesis/</code> &nbsp;BSc thesis: anonymising student documents</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/pii-anonymisation-thesis">pii-anonymisation-thesis/</a>
├── <a href="https://github.com/YannKleees/pii-anonymisation-thesis/tree/master/thesis_project">thesis_project/</a>      defender, attacker, training and experiments
├── <a href="https://github.com/YannKleees/pii-anonymisation-thesis/tree/master/document_generator">document_generator/</a>  synthetic student documents
├── <a href="https://github.com/YannKleees/pii-anonymisation-thesis/tree/master/notebooks">notebooks/</a>           one notebook per research question
├── <a href="https://github.com/YannKleees/pii-anonymisation-thesis/tree/master/UI">UI/</a>                  Streamlit demo and labelling tool
└── <a href="https://github.com/YannKleees/pii-anonymisation-thesis#readme">README.md</a>
</pre>

Layout-aware redaction of cover pages, tables and images. Recall 0.998 on 500 synthetic documents; a re-identification attacker's usable signals drop from 17.3 to 0.16 per document.
<br><sub>Python · GLiNER · OCR</sub> &nbsp; **[open repo →](https://github.com/YannKleees/pii-anonymisation-thesis)**

</details>

</blockquote>
</details>

<details>
<summary><b><code>computer-vision/</code></b> &nbsp;1 project</summary>
<blockquote>

<details>
<summary><code>orthodontic-par/</code> &nbsp;dental photos to PAR index suggestions</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/orthodontic-par">orthodontic-par/</a>
├── <a href="https://github.com/YannKleees/orthodontic-par/tree/master/ml">ml/</a>         YOLO11 training, inference and the Faster R-CNN comparison
├── <a href="https://github.com/YannKleees/orthodontic-par/tree/master/backend">backend/</a>    Express API, mosaic, PAR scoring, PDF reports
├── <a href="https://github.com/YannKleees/orthodontic-par/tree/master/frontend">frontend/</a>   React editor for the suggested boxes
├── <a href="https://github.com/YannKleees/orthodontic-par/tree/master/report">report/</a>     write-up of the follow-up on public data
└── <a href="https://github.com/YannKleees/orthodontic-par#readme">README.md</a>
</pre>

Started as an internship at LIST, rebuilt on the public OMNI dataset. YOLO11s reaches mAP50 0.697 on the test split, against 0.664 for the best model in the dataset paper.
<br><sub>PyTorch · YOLO11 · Node.js · React · TypeScript</sub> &nbsp; **[open repo →](https://github.com/YannKleees/orthodontic-par)**

</details>

</blockquote>
</details>

<details>
<summary><b><code>recommender-systems/</code></b> &nbsp;1 project</summary>
<blockquote>

<details>
<summary><code>job-recommender/</code> &nbsp;private</summary>
<br>

<pre>
job-recommender/        private: contains client data
├── two-tower retrieval
└── item-to-item retrieval
</pre>

Modular recommendation pipeline that matches candidates with jobs. Group project; I built most of the engine. Code on request.
<br><sub>Python · two-tower model · item-to-item</sub>

</details>

</blockquote>
</details>

<details>
<summary><b><code>research-reproduction/</code></b> &nbsp;1 project</summary>
<blockquote>

<details>
<summary><code>hyperreimpute/</code> &nbsp;reproduction of HyperImpute (ICML 2022)</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/hyperreimpute">hyperreimpute/</a>
├── <a href="https://github.com/YannKleees/hyperreimpute/blob/main/reproduction.ipynb">reproduction.ipynb</a>  every experiment, table and figure
├── <a href="https://github.com/YannKleees/hyperreimpute/tree/main/hyperreimpute">hyperreimpute/</a>      the code behind the notebook
├── <a href="https://github.com/YannKleees/hyperreimpute/tree/main/results">results/</a>            cached results, one CSV per experiment
├── <a href="https://github.com/YannKleees/hyperreimpute/tree/main/docs">docs/</a>               the report
└── <a href="https://github.com/YannKleees/hyperreimpute#readme">README.md</a>
</pre>

Reproduces Table 2 of the paper on three UCI datasets, checks the results against an older library version and tests the method's limits. A simple CatBoost baseline with fixed settings beat it.
<br><sub>Python · scikit-learn · CatBoost</sub> &nbsp; **[open repo →](https://github.com/YannKleees/hyperreimpute)**

</details>

</blockquote>
</details>

<details>
<summary><b><code>apps/</code></b> &nbsp;3 projects</summary>
<blockquote>

<details>
<summary><code>music-mystery/</code> &nbsp;music guessing game that adapts to the player</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/music-mystery">music-mystery/</a>
├── <a href="https://github.com/YannKleees/music-mystery/tree/master/src">src/</a>        Flask app, game logic, Deezer and MusicBrainz
├── <a href="https://github.com/YannKleees/music-mystery/tree/master/tests">tests/</a>
└── <a href="https://github.com/YannKleees/music-mystery#readme">README.md</a>
</pre>

HCI course project: a random and a personalised version for a user study, with an Elo rating per mode and an on-screen buddy that gives hints.
<br><sub>Python · Flask · SQLite</sub> &nbsp; **[open repo →](https://github.com/YannKleees/music-mystery)**

</details>

<details>
<summary><code>pizza-ordering-system/</code> &nbsp;pizza shop on a MySQL database</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/pizza-ordering-system">pizza-ordering-system/</a>
├── <a href="https://github.com/YannKleees/pizza-ordering-system/tree/master/customer_app">customer_app/</a>   menu, basket, discounts, loyalty, orders
├── <a href="https://github.com/YannKleees/pizza-ordering-system/tree/master/staff_app">staff_app/</a>      kitchen, deliveries, menu management, earnings
├── <a href="https://github.com/YannKleees/pizza-ordering-system/tree/master/db">db/</a>             16-table schema and example data
└── <a href="https://github.com/YannKleees/pizza-ordering-system#readme">README.md</a>
</pre>

Two desktop apps, one for customers and one for staff, on a shared relational schema.
<br><sub>Python · Tkinter · MySQL</sub> &nbsp; **[open repo →](https://github.com/YannKleees/pizza-ordering-system)**

</details>

<details>
<summary><code>wichtel/</code> &nbsp;Secret Santa draw for a group of friends</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/wichtel">wichtel/</a>
├── <a href="https://github.com/YannKleees/wichtel/blob/main/index.html">index.html</a>
├── <a href="https://github.com/YannKleees/wichtel/blob/main/draw.js">draw.js</a>     the draw
├── <a href="https://github.com/YannKleees/wichtel/blob/main/app.js">app.js</a>
└── <a href="https://github.com/YannKleees/wichtel/blob/main/style.css">style.css</a>
</pre>

Static site: everyone gets a private link that shows only their own match.
<br><sub>JavaScript · HTML · CSS</sub> &nbsp; **[open repo →](https://github.com/YannKleees/wichtel)**

</details>

</blockquote>
</details>

<details>
<summary><b><code>tools/</code></b> &nbsp;2 projects</summary>
<blockquote>

<details>
<summary><code>record/</code> &nbsp;records what your PC plays into separate, tagged tracks</summary>
<br>

<pre>
<a href="https://github.com/YannKleees/record">record/</a>
├── <a href="https://github.com/YannKleees/record/tree/main/record">record/</a>     recording engine and desktop UI
├── <a href="https://github.com/YannKleees/record/tree/main/tests">tests/</a>
├── <a href="https://github.com/YannKleees/record/blob/main/start.bat">start.bat</a>
└── <a href="https://github.com/YannKleees/record#readme">README.md</a>
</pre>

Works with any player that shows up in the Windows media controls; tracks are split and tagged with title, artist and cover art.
<br><sub>Python · pywebview · mutagen</sub> &nbsp; **[open repo →](https://github.com/YannKleees/record)**

</details>

<details>
<summary><code>datapluck/</code> &nbsp;private, in progress</summary>
<br>

<pre>
datapluck/          private, in progress
├── browser extension
└── chart-reading research
</pre>

Browser extension: click a table or chart on a web page and copy its data as CSV or pandas code.
<br><sub>TypeScript · tesseract.js · Playwright</sub>

</details>

</blockquote>
</details>

</blockquote>
</details>

<p>
<a href="https://www.linkedin.com/in/yann-klees-a0b8a6334"><code>linkedin</code></a> &nbsp;
<a href="mailto:yannklees@gmail.com"><code>yannklees@gmail.com</code></a>
</p>
