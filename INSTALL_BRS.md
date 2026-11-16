# Install: ILISCyber BRS skill (instructions for Copilot)

Add this package to the user-manual repository root as follows:

1. Copy these files into the repository, keeping their folders:
   - `.github/skills/iliscyber-brs/` (SKILL.md and references/)
   - `tools/brs_img.py`
   - `tools/brs_docx.py`
   - `tools/brs_plan.py`
   - `template/BRS_Sample_Accept_Release.docx`
   - `work/brs/.gitkeep`
   - `output/brs/.gitkeep`
2. In `requirements.txt`, add the line `python-docx>=1.1`. Keep the existing lines.
3. In `.github/copilot-instructions.md`, add this bullet after the first one:
   `- When the user asks for a BRS (Business Requirement Specification), use the skill iliscyber-brs. Its tools are python tools/brs_img.py and python tools/brs_docx.py, alongside tools/ilis.py.`
4. In `.github/workflows/copilot-setup-steps.yml`, make sure `pip install -r requirements.txt` runs. It already does if the workflow installs requirements.
5. Run the checks:
   - `python tools/brs_img.py -h`
   - `python tools/brs_docx.py inspect template/BRS_Sample_Accept_Release.docx`
6. Commit the changes in a pull request titled "Add ILISCyber BRS skill".

`brs_img.py` imports `tools/ilis_img.py` from the existing toolkit, so it must sit next to it in `tools/`.

Note: `tools/brs_plan.py` imports `tools/ilis_gui.py` from the existing toolkit.
