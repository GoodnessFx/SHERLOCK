# Contributing to SHERLOCK 🕵️‍♂️

First off, thank you for considering contributing to SHERLOCK! It's people like you that make SHERLOCK such a powerful tool for the prediction market community.

## 🤝 Code of Conduct
By participating in this project, you agree to abide by our terms:
- Be respectful and professional.
- Focus on technical improvements and edge detection accuracy.
- Maintain the "Dark Terminal Luxury" aesthetic in all UI contributions.

## 🛠 How Can I Contribute?

### Reporting Bugs
- Use the GitHub Issues tab.
- Describe the bug and provide steps to reproduce it.
- Include your environment details (Python version, OS, etc.).

### Suggesting Enhancements
- If you have an idea for a new signal source (e.g., specific sports APIs, election trackers), open an issue first.
- For UI changes, remember the aesthetic: **pure black, matrix green, and amber highlights.** No purple gradients. No generic SaaS look.

### Pull Requests
1. **Fork the repo** and create your branch from `main`.
2. **Implement your changes.** Ensure you follow the project's coding style (use `make lint`).
3. **Add tests.** If you're adding a new core module or agent, include a test file in `tests/`.
4. **Update the README** if you're adding new configuration variables.
5. **Issue a PR.** Provide a clear description of what you've added or fixed.

## 🏗 Development Environment
1. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/SHERLOCK.git
   cd SHERLOCK
   ```
2. **Install dev dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install black ruff pytest
   ```
3. **Run tests:**
   ```bash
   make test
   ```

## 🎨 UI/UX Standards
- **Fonts:** "Space Mono" for data, "Syne" for headings.
- **Colors:**
  - Primary: `#00FF41` (Green)
  - Accent: `#F59E0B` (Amber)
  - Background: `#000000` (Pure Black)
- **Effects:** Glassmorphism, subtle grid overlays, scanline textures.

## 📜 License
By contributing, you agree that your contributions will be licensed under its MIT License.

---

*Let's build the autonomous intelligence network that never sleeps.*
