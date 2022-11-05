var toggle_ad = function(e)
{
	e.preventDefault()
	ad_ele = gradioApp().querySelector("#unprompted #ad");
	ad_ele.classList.toggle("active")

	if (ad_ele.classList.contains("active")) this.innerHTML = "Dismiss";
	else this.innerHTML = "Show Ad";
}

onUiUpdate(function()
{
	var buttons = gradioApp().querySelectorAll("#unprompted #toggle-ad");
	buttons.forEach(function(btn)
	{
		btn.addEventListener("click",toggle_ad,true)
	})
});