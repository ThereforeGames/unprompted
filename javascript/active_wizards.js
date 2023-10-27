/**
 * Give a badge on Unprompted Accordion indicating total number of active 
 * wizard scripts.
*/
(function()
{
	const unprompted_accordions = new Set();

	function update_active_unit_count(accordion)
	{
		const span = accordion.querySelector(".label-wrap span");
		let active_unit_count = 0;
		accordion.querySelectorAll(".wizard-autoinclude input").forEach(function(checkbox)
		{
			if (checkbox.checked)
			{
				console.log("found checkbox");
				active_unit_count++;
			}
		});

		if (span.childNodes.length !== 1)
		{
			span.removeChild(span.lastChild);
		}
		if (active_unit_count > 0)
		{
			const div = document.createElement("div");
			div.classList.add("unprompted-badge");
			div.innerHTML = `🪄 ${active_unit_count} wizard${active_unit_count > 1 ? "s" : ""}`;
			span.appendChild(div);
		}
	}

	onUiUpdate(() =>
	{
		gradioApp().querySelectorAll(".unprompted-accordion").forEach(function(accordion)
		{
			if (unprompted_accordions.has(accordion)) return;
			accordion.querySelectorAll(".wizard-autoinclude input").forEach(function(checkbox)
			{
				checkbox.addEventListener("change", function()
				{
					update_active_unit_count(accordion);
				});
			});
			unprompted_accordions.add(accordion);
		});
	});
})();