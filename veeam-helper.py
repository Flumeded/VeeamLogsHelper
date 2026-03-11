import sublime
import sublime_plugin
import re
import os
import threading
import importlib

# ---------------------------------------------------------------------------
# Docs import — use package-relative import so it works regardless of where
# the package folder is installed.
# ---------------------------------------------------------------------------
_PACKAGE = __name__.split('.')[0]
_docs_mod = importlib.import_module(f'{_PACKAGE}.veeam_docs')
OPTION_DOCS = _docs_mod.OPTION_DOCS

# ---------------------------------------------------------------------------
# Cache
# Keyed by folder path. Filled once when a Job log is opened; evicted when
# no more log files from that folder are open.
# ---------------------------------------------------------------------------
_cache = {}          # { folder: { 'loaded': bool, 'agent_starts': [], 'agent_sessions': [] } }
_cache_lock = threading.Lock()


def _is_job_log(filename):
    return bool(re.match(r'Job\..+\.log$', os.path.basename(filename), re.IGNORECASE))


def _fill_cache(folder):
    """Scan job log files in *folder* and populate the cache entry.
    Runs on a background thread."""
    # Placeholder — agent lookup will be implemented in a later iteration.
    with _cache_lock:
        _cache[folder] = {
            'loaded':          True,
            'agent_starts':    [],
            'agent_sessions':  [],
        }


def _evict_if_unused(folder):
    """Remove the cache entry for *folder* if no open views reference it."""
    open_folders = {
        os.path.dirname(v.file_name())
        for w in sublime.windows()
        for v in w.views()
        if v.file_name()
    }
    if folder not in open_folders:
        with _cache_lock:
            _cache.pop(folder, None)


# ---------------------------------------------------------------------------
# Event listener
# ---------------------------------------------------------------------------
class VeeamEventListener(sublime_plugin.EventListener):

    # -- Cache lifecycle -----------------------------------------------------

    def on_load_async(self, view):
        filename = view.file_name()
        if not filename or not _is_job_log(filename):
            return
        folder = os.path.dirname(filename)
        with _cache_lock:
            already = folder in _cache
        if not already:
            with _cache_lock:
                _cache[folder] = {'loaded': False, 'agent_starts': [], 'agent_sessions': []}
            threading.Thread(target=_fill_cache, args=(folder,), daemon=True).start()

    def on_close(self, view):
        filename = view.file_name()
        if not filename:
            return
        # Defer eviction slightly so the view is fully removed first.
        sublime.set_timeout(lambda: _evict_if_unused(os.path.dirname(filename)), 500)

    # -- Hover ---------------------------------------------------------------

    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return
        filename = view.file_name()
        if not filename or not filename.lower().endswith('.log'):
            return

        # 1. Option name lookup (works in both XML and bracket-format lines)
        word = view.substr(view.word(point))
        if word in OPTION_DOCS:
            self._show_option_popup(view, point, word)
            return

        # 2. Agent digest lookup — placeholder for future implementation.

    def _show_option_popup(self, view, point, option_name):
        doc = OPTION_DOCS[option_name]
        body = (
            '<body id="veeam-option-doc">'
            '<style>'
            '  body { font-family: sans-serif; font-size: 0.9em; margin: 6px; }'
            '  .name { font-weight: bold; color: var(--yellowish); }'
            '  .doc  { margin-top: 4px; }'
            '</style>'
            f'<div class="name">{option_name}</div>'
            f'<div class="doc">{doc}</div>'
            '</body>'
        )
        view.show_popup(
            body,
            location=point,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            max_width=600,
        )


# ---------------------------------------------------------------------------
# Command: format Job Options XML into a new scratch view
# ---------------------------------------------------------------------------
class VeeamFormatXmlCommand(sublime_plugin.TextCommand):
    """Extract and pretty-print the Job Options XML from the current line.

    Bind to a key in your keymap:
        { "keys": ["ctrl+shift+x"], "command": "veeam_format_xml" }
    """

    def run(self, edit):
        view   = self.view
        point  = view.sel()[0].begin()
        line   = view.substr(view.line(point))

        match = re.search(r'(<JobOptionsRoot>.+?</JobOptionsRoot>)', line)
        if not match:
            sublime.status_message('Veeam: no Job Options XML found on this line.')
            return

        import xml.dom.minidom
        try:
            pretty = xml.dom.minidom.parseString(match.group(1)).toprettyxml(indent='    ')
            # Drop the <?xml ...?> declaration line.
            pretty = '\n'.join(pretty.splitlines()[1:])
        except Exception as e:
            sublime.status_message(f'Veeam: XML parse error — {e}')
            return

        new_view = view.window().new_file()
        new_view.set_name('Job Options XML')
        new_view.set_scratch(True)
        new_view.assign_syntax('Packages/XML/XML.sublime-syntax')
        new_view.run_command('append', {'characters': pretty})
