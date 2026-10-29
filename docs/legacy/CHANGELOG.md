# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project adheres to Semantic Versioning.

## [v1.1.0] - 2025-10-12

### Added
- QUICKSTART.md: 15-minute setup with 5-command fast path
- COMMANDS.md: Beginner-friendly commands with Windows/macOS/Linux variants
- TUTORIAL.md: Complete beginner-to-advanced learning path
- ARCHITECTURE.md: Plain-language architecture with diagrams and data flow
- CONFIG_DOCS.md: Line-by-line configuration explanations
- Documentation Index in README linking all guides

### Changed
- README.md: Overhauled with simple explanations, cross-platform setup, and dashboards guide
- logstash/pipeline/logstash.conf: Improved parsing and pipeline clarity
- entrypoint.sh: More robust service startup and logging
- Dockerfile: Minor touch-ups for build clarity

### Removed
- Simulation/test utilities: adaptive_response_simulator.py, network_traffic_simulator.py, stealth_monitor.py, user_behavior_simulator.py, dynamic_file_updater.py, list_gemini_models.py
- Generated artifacts and caches: generated_files/, __pycache__/, nohup.out

### Notes
- No breaking changes expected
- Start here: QUICKSTART.md → TUTORIAL.md → COMMANDS.md → Kibana Data View


## [v1.0.0] - 2025-10-10

### Added
- Initial working honeypot with ELK integration
- Basic README and setup
