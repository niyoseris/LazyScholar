# Research Roadmap Feature

## Description
This PR adds a new feature to generate a structured research roadmap before starting the research process. The roadmap serves as a planning document outlining research objectives, methodology, timeline, and expected outcomes.

## Changes
- Added `roadmap_generator.py` to create research roadmaps in Markdown format
- Updated `main.py` to integrate roadmap generation in the research workflow
- Enhanced `ui_module.py` to better handle non-interactive input

## Implementation Details
- Roadmap is generated after topics/subtopics but before literature search
- Uses Gemini API to generate detailed roadmap content when available
- Falls back to a template-based approach when API is unavailable
- Saves roadmap to `research_results/roadmap.md`

## Testing
- Tested in demo mode with sample problem statements
- Verified roadmap generation with different topic formats
- Ensured proper error handling for non-interactive input

## Benefits
- Provides researchers with a structured plan before starting research
- Helps identify methodological approaches for each topic
- Establishes clear research objectives and timeline
- Anticipates challenges and proposes mitigation strategies

## Future Improvements
- Add option to customize roadmap templates
- Enable user editing of roadmap before proceeding
- Integrate roadmap milestones with actual research progress
- Generate topic-specific research methodologies
