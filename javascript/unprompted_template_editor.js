function loadFile(file_name)
{
	// print the filename to the console
	console.log(file_name);
	var textarea = gradioApp().querySelector("#save_name > label > textarea");
	textarea.value = file_name;
	console.log(textarea);

	updateInput(textarea);
	// wait 200 ms for the event to process then click the load button
	setTimeout(clickLoad, 200);
}

function clickLoad()
{
	var loadFileButton = document.getElementById("load_button_unprompted");
	loadFileButton.click();

}
function registerPrompt(tabname, id)
{
	var textarea = gradioApp().querySelector("#" + id + " > label > textarea");

	if (!activePromptTextarea[tabname])
	{
		activePromptTextarea[tabname] = textarea;
	}

	textarea.addEventListener("focus", function()
	{
		activePromptTextarea[tabname] = textarea;
	});
}

function unpromptedStartup()
{
	console.log("We are in unprompted startup");
	var refreshButton = document.getElementById("refresh_button_unprompted");
	refreshButton.click();
	setupExtraNetworksForTab('unprompted_edit_space');
	registerPrompt('unprompted_edit_space', 'unprompted_edit_space_prompt');
}

addEventListener('click', (event) =>
{

	let target = event.originalTarget || event.composedPath()[0];
	// check if the thing we clicked on it s button with the word unprompted in the content
	if (!target.matches("button")) return;
	if (!target.textContent.includes("Unprompted")) return;
	if (!target.textContent.includes("Editor")) return;
	loaded_unprompted_template_edit = true;
	unpromptedStartup(event);
});