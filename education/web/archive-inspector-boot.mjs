/** Do not initialize an archived anatomical worker on page load. */
const configuration = document.querySelector('script[data-archive-entry]');
if (!configuration || configuration.dataset.archiveEntry !== 'inspect.js') throw Error('Unknown inspector entry');
const launch = document.createElement('button');
launch.id = 'launch-archive-runtime';
launch.type = 'button';
launch.textContent = 'Load archived computational inspector';
const note = document.createElement('p');
note.id = 'archive-runtime-status';
note.setAttribute('role', 'status');
note.textContent = 'Static historical evidence and downloads are available. The archived numerical worker has not started.';
const main = document.querySelector('main');
if (!main) throw Error('Missing inspector main');
const controls = [...main.querySelectorAll('button,input,select')];
const disabled = controls.map(control => control.disabled);
controls.forEach(control => { control.disabled = true; });
main.prepend(launch, note);
launch.addEventListener('click', async () => {
  launch.disabled = true;
  note.textContent = 'Loading the archived computational model. This release has not requalified its solver.';
  try {
    await import(new URL(configuration.dataset.archiveEntry, location.href).href);
    controls.forEach((control, i) => { control.disabled = disabled[i]; });
    note.textContent = 'Archived model loaded. Read its historical limitations before running a step.';
  } catch (error) {
    note.textContent = 'Archived model unavailable: ' + error.message + '. Historical evidence and downloads remain available.';
    launch.disabled = false;
  }
});
