"""Exercise the research-book reading dock on a bounded, explicitly labelled preview.

This gate checks the actual reader and embedded controls. It does not run a
scientific campaign, compile Lean, qualify a release, or publish anything.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import argparse
import hashlib
import json
import os
import shutil

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def wait_example(page, chapter, parameters=None):
    expect(page.locator('.reading-example-frame')).to_have_count(1)
    page.frame_locator('.reading-example-frame').locator('#example-choice').wait_for(state='attached')
    frame = next(f for f in page.frames if 'examples.html' in f.url)
    frame.wait_for_function(
        '(chapter) => window.kenomaChapterExample?.ready && kenomaChapterExample.example.id === chapter',
        arg=chapter, timeout=90000)
    if parameters:
        frame.wait_for_function(
            '(wanted) => Object.entries(wanted).every(([key, value]) => kenomaChapterExample.parameters[key] === value)'
            ' && Object.entries(wanted).every(([key, value]) => !kenomaChapterExample.state || kenomaChapterExample.state.parameters[key] === value)',
            arg=parameters, timeout=90000)
    return frame


def step_id(step):
    return step.get('id') or step.get('step')


def show_step(page, chapter, step):
    target = page.locator(f'.teaching-step[data-teaching-chapter="{chapter}"][data-teaching-step="{step_id(step)}"]')
    expect(target).to_have_count(1)
    target.locator('[data-show-step]').click()
    try:
        page.wait_for_function(
            '([chapter, step]) => window.kenomaResearchBook?.chapter === chapter && kenomaResearchBook.step === step',
            arg=[chapter, step_id(step)])
        return wait_example(page, chapter, step.get('parameters'))
    except Exception:
        print('FAILED STEP', chapter, step_id(step), page.evaluate(
            '({chapter:kenomaResearchBook.chapter,step:kenomaResearchBook.step,following:kenomaResearchBook.following,scrollY})'), flush=True)
        raise


def click_visible(page, selector):
    """Use actual pointer input for an already-visible sticky toolbar control.

    Chromium's scrollIntoViewIfNeeded can scroll a long document when Playwright
    tries to click a sticky button that is already on screen. Hit testing avoids
    introducing that automation-only scroll and still requires a real click.
    """
    control = page.locator(selector)
    expect(control).to_be_visible()
    rect = control.bounding_box()
    x, y = rect['x'] + rect['width'] / 2, rect['y'] + rect['height'] / 2
    assert control.evaluate('(e, point) => e.contains(document.elementFromPoint(...point))', [x, y])
    page.mouse.click(x, y)


def no_overflow(page):
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), 'Reader overflows viewport'
    frame = next((f for f in page.frames if 'examples.html' in f.url), None)
    if frame:
        assert not frame.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), 'Embedded example overflows viewport'


def snapshot(page, output, name):
    no_overflow(page)
    page.screenshot(path=str(output / (name + '.png')))


def run(site, output):
    site = site.resolve()
    output.mkdir(parents=True, exist_ok=True)
    sequences = json.loads((site / 'teaching-sequences.json').read_text())
    lessons = sequences['lessons']
    assert len(lessons) == 27
    by_chapter = {lesson['chapter']: lesson for lesson in lessons}
    inputs = [site / p for p in ['index.html', 'examples.html', 'teaching-sequences.json',
              'chapter-examples.json', 'assets/research-book.css', 'assets/book-interaction.js',
              'assets/chapter-examples.js', 'assets/chapter-worker.js']]
    before = {str(p.relative_to(site)): digest(p) for p in inputs}
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(site.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/{site.name}/'
    receipt = {'scope': 'Browser interaction and rendering only; no new solver, proof, PDF or release qualification.',
               'result': 'PASS_RESEARCH_BOOK_PREVIEW_BROWSER', 'inputSha256': before,
               'testSha256': digest(Path(__file__)), 'views': []}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'),
                args=['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
            receipt['browser'] = browser.version
            for name, width, height in [('desktop', 1440, 1000), ('phone', 390, 844), ('narrow', 320, 844)]:
                page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
                page.add_init_script("""window.__readingMessages = []; window.__manualMessages = [];
                    addEventListener('message', event => {
                        if (event.origin === location.origin && event.source === parent &&
                            event.data?.type === 'kenoma:set-step')
                            __readingMessages.push(structuredClone(event.data));
                        if (event.origin === location.origin && event.data?.type === 'kenoma:manual')
                            __manualMessages.push(structuredClone(event.data));
                    });""")
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(base, wait_until='domcontentloaded')
                page.wait_for_function('!!window.kenomaResearchBook')
                assert page.locator('.teaching-step').count() == sum(len(x['steps']) for x in lessons)
                if width >= 1100:
                    expect(page.locator('#example-dock')).to_be_visible()
                else:
                    expect(page.locator('#book-toolbar')).to_be_visible()
                    expect(page.locator('#example-dock')).not_to_be_visible()
                    expect(page.locator('.reading-example-frame')).to_have_count(0)
                    page.locator('#toggle-contents').click()
                    expect(page.locator('#toggle-contents')).to_have_attribute('aria-expanded', 'true')
                    expect(page.locator('#book-contents')).to_be_visible()
                    menu = page.locator('#book-contents')
                    rect = menu.bounding_box()
                    assert rect['y'] >= 0 and rect['y'] + rect['height'] <= height + 1, 'Chapter drawer must stay within the phone viewport'
                    menu.locator('a:visible').last.scroll_into_view_if_needed()
                    last_rect = menu.locator('a:visible').last.bounding_box()
                    assert last_rect['y'] >= 0 and last_rect['y'] + last_rect['height'] <= height + 1, 'Last chapter link must be reachable inside the drawer'
                    page.locator('#toggle-contents').click()
                    expect(page.locator('#toggle-contents')).to_have_attribute('aria-expanded', 'false')
                selected = lessons if name == 'desktop' else [by_chapter[x] for x in ['01-force', '02-torque', '03-energy', '10b-pressure-projection']]
                checked = []
                for lesson in selected:
                    for step in lesson['steps'] if name == 'desktop' else [lesson['steps'][0], lesson['steps'][-1]]:
                        frame = show_step(page, lesson['chapter'], step)
                        no_overflow(page)
                        if frame.evaluate('!!kenomaChapterExample.viewport'):
                            frame.wait_for_function('kenomaChapterExample.viewport.webgl.info.render.calls > 0')
                            expect(frame.locator('#example-viewport canvas')).to_have_count(1)
                            if lesson['chapter'] == '01-force':
                                assert frame.evaluate("""() => {
                                    const v = kenomaChapterExample.viewport;
                                    return kenomaChapterExample.state.objects.filter(o => o.type === 'sphere').every(o => {
                                        const p = v.camera.position.clone().fromArray(o.center).project(v.camera);
                                        return Math.abs(p.x) < .98 && Math.abs(p.y) < .98 && Math.abs(p.z) < 1;
                                    });
                                }"""), 'Force origin/current marker left the visible scene at ' + step_id(step)

                        checked.append({'chapter': lesson['chapter'], 'step': step_id(step), 'parameters': frame.evaluate('kenomaChapterExample.parameters')})
                        print(name, lesson['chapter'], step_id(step), 'PASS', flush=True)
                force = by_chapter['01-force']
                frame = show_step(page, '01-force', force['steps'][0])
                # A real keyboard edit pauses following. Scrolling into another
                # chapter must preserve both user state and iframe focus.
                field = frame.locator('#parameter-force')
                prior_message = frame.evaluate('__readingMessages.at(-1)')
                assert prior_message, 'The embedded example must have received an actual reading update'
                field.fill('8')
                frame.wait_for_function('kenomaChapterExample.state.parameters.force === 8')
                page.wait_for_function('!kenomaResearchBook.following')
                prior_manual = page.evaluate('__manualMessages.at(-1)')
                expect(page.locator('#follow-reading')).to_have_attribute('aria-pressed', 'false')
                # Replay an actual reading message after the edit. A message
                # already in transit must not overwrite a local manual hold.
                message_count = frame.evaluate('__readingMessages.length')
                page.evaluate('(message) => document.querySelector(".reading-example-frame").contentWindow.postMessage(message, location.origin)', prior_message)
                frame.wait_for_function('(count) => __readingMessages.length > count', arg=message_count)
                assert frame.evaluate('kenomaChapterExample.parameters.force') == 8, 'A stale automatic update overwrote the manual edit'
                assert frame.evaluate('document.activeElement.id') == 'parameter-force'
                other = by_chapter['02-torque']['steps'][0]
                page.locator(f'#step-02-torque-{step_id(other)}').evaluate('(e) => e.scrollIntoView({block:"start"})')
                page.wait_for_function('kenomaResearchBook.chapter === "02-torque"')
                assert frame.evaluate('kenomaChapterExample.example.id') == '01-force'
                assert frame.evaluate('kenomaChapterExample.parameters.force') == 8
                assert frame.evaluate('document.activeElement.id') == 'parameter-force'
                frame.locator('#reset-example').click()
                wait_example(page, '01-force', force['steps'][0]['parameters'])
                assert not page.evaluate('kenomaResearchBook.following')
                frame.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
                assert frame.evaluate('scrollY > 0'), 'Fixture must begin with an internally scrolled child'
                page.locator('#follow-reading').click()
                page.wait_for_function('kenomaResearchBook.following')
                frame = wait_example(page, '02-torque', other.get('parameters'))
                manual_count = page.evaluate('__manualMessages.length')
                frame.evaluate('(message) => parent.postMessage(message, location.origin)', prior_manual)
                page.wait_for_function('(count) => __manualMessages.length > count', arg=manual_count)
                assert page.evaluate('kenomaResearchBook.following'), 'A stale manual pause cancelled explicit Follow reading'
                frame.wait_for_function('scrollY === 0')
                assert frame.locator('#example-viewport canvas').evaluate(
                    '(e) => {const r=e.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight + 1;}'), 'New chapter scene must be fully visible'

                # The normal scroll route selects the next worked stop.
                energy = by_chapter['03-energy']
                target = page.locator(f'#step-03-energy-{step_id(energy["steps"][-1])}')
                target.evaluate('(e) => e.scrollIntoView({block:"start"})')
                page.wait_for_function('kenomaResearchBook.chapter === "03-energy"')
                frame = wait_example(page, '03-energy', energy['steps'][-1].get('parameters'))
                snapshot(page, output, f'after-{name}-energy')
                # Rapid changes must finish on the most recent reading stop.
                for chapter in ['01-force', '02-torque', '10b-pressure-projection']:
                    step = by_chapter[chapter]['steps'][0]
                    page.locator(f'#step-{chapter}-{step_id(step)}').evaluate('(e) => e.scrollIntoView({block:"start"})')
                projection = by_chapter['10b-pressure-projection']
                page.wait_for_function('kenomaResearchBook.chapter === "10b-pressure-projection"')
                frame = wait_example(page, '10b-pressure-projection', projection['steps'][0].get('parameters'))
                snapshot(page, output, f'after-{name}-projection')
                # Closing really disposes the frame. Reopening applies current reading.
                if width < 1100:
                    reading_scroll = page.evaluate('scrollY')
                    page.locator('#close-example').click()
                    expect(page.locator('.reading-example-frame')).to_have_count(0)
                    click_visible(page, '#toggle-example')
                    frame = wait_example(page, '10b-pressure-projection', projection['steps'][0].get('parameters'))
                    assert abs(page.evaluate('scrollY') - reading_scroll) <= 1, 'Closing/reopening must preserve the reading position'

                frame = show_step(page, '01-force', force['steps'][-1])
                canvas = frame.locator('#example-viewport canvas')
                canvas.focus()
                position = frame.evaluate('kenomaChapterExample.viewport.camera.position.toArray()')
                page.keyboard.press('ArrowLeft')
                assert frame.evaluate('kenomaChapterExample.viewport.camera.position.toArray()') != position
                page.wait_for_function('!kenomaResearchBook.following')
                snapshot(page, output, f'after-{name}-force')
                # Wheel zoom alone must suspend following, without requiring a click.
                page.locator('#follow-reading').click()
                page.wait_for_function('kenomaResearchBook.following')
                canvas.hover()
                position = frame.evaluate('kenomaChapterExample.viewport.camera.position.toArray()')
                page.mouse.wheel(0, 100)
                page.wait_for_function('!kenomaResearchBook.following')
                frame.wait_for_function('(before) => JSON.stringify(kenomaChapterExample.viewport.camera.position.toArray()) !== JSON.stringify(before)', arg=position)
                # An unrelated sender cannot pause the dock or alter its lesson.
                previous_generation = frame.evaluate('__readingMessages.at(-1).generation')
                page.locator('#follow-reading').click()
                page.wait_for_function('kenomaResearchBook.following')
                frame.wait_for_function('(generation) => __readingMessages.at(-1).generation > generation', arg=previous_generation)
                valid_generation = frame.evaluate('__readingMessages.at(-1).generation')
                page.evaluate('(generation) => dispatchEvent(new MessageEvent("message",{origin:location.origin,source:window,data:{type:"kenoma:manual",generation}}))', valid_generation)
                assert page.evaluate('kenomaResearchBook.following')
                # Compact claim disclosure remains keyboard operable.
                button = page.locator('.claim-toggle').first
                body = page.locator('.claim-technical').first
                expect(body).not_to_be_visible()
                button.focus()
                page.keyboard.press('Enter')
                expect(body).to_be_visible()
                page.keyboard.press('Space')
                expect(body).not_to_be_visible()
                page.emulate_media(media='print')
                expect(body).to_be_visible()
                expect(page.locator('#example-dock')).not_to_be_visible()
                page.emulate_media(media='screen')
                assert not errors, errors
                receipt['views'].append({'name': name, 'width': width, 'height': height, 'stepsChecked': checked,
                    'manualStateAndFocusPreserved': True, 'manualResetToSelectedStep': True, 'scrollFollowResume': True,
                    'rapidScrollLatestWins': True, 'closeReopen': width < 1100, 'keyboardOrbit': True,
                    'wheelAlonePausesFollowing': True, 'newChapterSceneScrollReset': True,
                    'staleAutomaticUpdateRejected': True,
                    'staleManualPauseRejectedAfterResume': True,
                    'unrelatedSenderRejected': True, 'proofDisclosureAndPrint': True, 'pageErrors': errors})
                page.close()
            page = browser.new_page(java_script_enabled=False, viewport={'width': 390, 'height': 844})
            page.goto(base)
            expect(page.locator('.claim-technical').first).to_be_visible()
            expect(page.locator('#book-toolbar')).not_to_be_visible()
            assert page.locator('.teaching-step').count() == sum(len(x['steps']) for x in lessons)
            assert page.locator('.chapter-example a').count() >= len(lessons)
            no_overflow(page)
            receipt['noJavascriptReading'] = True
            page.close()
            # Context loss keeps numerical controls usable and clearly labelled.
            page = browser.new_page(viewport={'width': 1440, 'height': 1000})
            page.goto(base)
            page.wait_for_function('!!window.kenomaResearchBook')
            frame = show_step(page, '01-force', by_chapter['01-force']['steps'][0])
            frame.evaluate("kenomaChapterExample.viewport.webgl.getContext().getExtension('WEBGL_lose_context').loseContext()")
            expect(frame.locator('#example-viewport')).to_contain_text('context lost')
            frame.locator('#parameter-force').fill('8')
            frame.wait_for_function('kenomaChapterExample.state.parameters.force === 8')
            receipt['contextLossNumericalFallback'] = True
            page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    assert before == {str(p.relative_to(site)): digest(p) for p in inputs}, 'Delivered UI changed during browser review'
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'review/research-book-teaching')
    args = parser.parse_args()
    run(args.site, args.output)
