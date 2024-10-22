# Bug fix log
Doing this because I end up finding I already solved the problem somewhere already and failed to update it in another section of code
- Caption Dialog causing crash - 10/09/2024
  - How : Opening caption dialog -> Close dialog -> Change results via submit/import
  - Fix : Connect caption dialog model_changed to IGW modelChanged signal:
    -     self.parent().modelChanged.connect(caption_window.model_changed)
