import sublime, sublime_plugin
import re

# TODO: move to config
placeholder_dictionary = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# FIXME: variable shared across all windows
placeholer_positions = {}

SPECIAL_CHARACTERS = [
  '[', ']',
  '(', ')',
  '\\', '+', '*', '^', '$', '?', '|',  '.'

]

class JumpPrepareCommand(sublime_plugin.TextCommand):
  def run(self, edit, character=None):
    # clear old placeholer positions
    placeholer_positions.clear()

    placeholder_regions = []
    current_character_placeholder_id = 0

    view = sublime.active_window().active_view()

    # set "jumping" flag for key binding context
    view.settings().set('jumping', True)

    visible_region = view.visible_region()
    visible_text = view.substr(visible_region)
    visible_region_offset = visible_region.begin()

    if character in SPECIAL_CHARACTERS:
      character = '\\' + character

    # iterate all matched characters in visible region
    for character_position in (match.start() for match in re.finditer(character, visible_text)):
      # if dictionary has already ended
      if current_character_placeholder_id == len(placeholder_dictionary):
        break

      absolute_character_position = character_position + visible_region_offset

      placeholder_region = sublime.Region(absolute_character_position,
        absolute_character_position + 1)

      placeholder_regions.append(placeholder_region)

      # replace with character from placeholder dictionary
      view.replace(edit, placeholder_region,
        placeholder_dictionary[current_character_placeholder_id])

      # store absolute position of placeholder character
      placeholer_positions[placeholder_dictionary[current_character_placeholder_id]] \
        = sublime.Region(absolute_character_position)

      current_character_placeholder_id += 1

    view.add_regions('jumping', placeholder_regions, 'string')

class JumpCommand(sublime_plugin.WindowCommand):
  def run(self, character):
    view = self.window.active_view()

    self.window.active_view().run_command("undo")

    view.settings().set('jumping', False)

    if character in placeholer_positions:
      view.sel().clear()
      view.sel().add(placeholer_positions[character])

class JumpCancelCommand(sublime_plugin.WindowCommand):
  def run(self):
    view = self.window.active_view()

    view.run_command('undo')

    view.settings().set('jumping', False)
