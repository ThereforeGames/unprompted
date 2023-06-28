<details><summary>Getting Started</summary>

Your first Unprompted template. It's a big step, I know. You feeling nervous? A sense of tremendous pressure maybe? Don't worry, it's not that hard to set this thing up.

For the purposes of this guide, we will construct a basic "human generator" similar to the one that is included with the repo download.

<details><summary>Step 1: Create the entry point</summary>

In the root directory of the WebUI app, navigate to `extensions/unprompted/templates`. This is where all your templates belong - you can organize the files here in any way you like.

Create a blank text file called `example.txt`. This will serve as the "entry point" for our new template.

Open up your new file and enter the following text:

```
Photo of a man
```

Save the file and boot up your Unprompted interface. I will be using [Automatic's repo](https://github.com/AUTOMATIC1111/stable-diffusion-webui) for this guide, but you can follow along with the standalone `unprompted_dry.py` if you prefer.

Now enter the following as your prompt and press generate:

```
[file example]
```

You can check the information underneath the resulting picture to confirm that Stable Diffusion received the correct prompt ("Photo of a man").

![image](https://user-images.githubusercontent.com/95403634/198932275-a9072004-15ab-4076-81a4-9d5e059a0084.png)

Cool! Now let's proceed to the good stuff...

</details>

<details><summary>Step 2: Using the [choose] shortcode</summary>

Let's ask Unprompted to choose between a man and a woman. This is easy to do:

```
Photo of a [choose]man|woman[/choose]
```

> **💡 Tip:** All of the code in this guide refers to our example.txt file unless otherwise noted. Remember to save your file with each change!

> **💡 Tip:** You do NOT need to restart the web UI when making changes to your text files.

We can use the vertical pipe (i.e. `|`) to separate our options.

Now, what if we want to specify the hair color for our subject? We could do something like this...

`Photo of a [choose]red|blue|yellow|green[/choose]-haired [choose]man|woman[/choose]`

...but as you can imagine, the list of options can become quite lengthy and difficult to manage. There's a better way. **We will create a separate file called `color.txt` and put our colors there.** In programming, this is akin to an "object-oriented approach."

To make our life even easier, we can put our options on individual lines instead of relying on the vertical pipe.

So here's our new `color.txt`:

```
[choose]
red
blue
yellow
green
pink
[/choose]
```

Feel free to add a bunch of other colors - I'm keeping things brief for the guide.

Now, we can reference our new file in `example.txt` like this:

`Photo of a [file color]-haired [choose]man|woman[/choose]`

Yes, we are using a `[file]` shortcode inside of another file. This is perhaps one of the most powerful things about Unprompted!

![image](https://user-images.githubusercontent.com/95403634/198935189-03a671ab-1449-48b8-a5c7-ddc7855ae26b.png)

Next, let's check out some other shortcodes we can use.

</details>

<details><summary>Step 3: Managing Stable Diffusion options with [set]</summary>

Unprompted has the ability to manage variables using `[set]` and `[get]`. You can create your own variables or even adjust the system variables used by the image generator.

At the bottom of `example.txt`, let's force a seed value of "1" to help with later debugging:

```
[set seed]1[/set]
```

For improved image quality, we can also force a CFG scale of 7 and turn on the "Restore Faces" option:

```
[set cfg_scale]7[/set]
[set restore_faces]1[/set]
```

Now no matter how we change the UI, our template will continue using these optimized values.

</details>

<details><summary>Step 4: Overriding parts of the template</summary>

Imagine a situation where you want the randomness a template offers, but you need to lock in a certain word or phrase of your choosing.

For example, maybe we want to generate a "panda" instead of a "man" or "woman." Do we have to destructively edit our template file? No! We can use the `[override]` shortcode for this. Here's how:

In `example.txt`, we need to wrap the man/woman phrase with a variable that will act like a category:

```
[set subject _out][choose]man|woman[/choose][/set]
```

I'm calling this variable `subject` but you can name it anything you like.

The `_out` argument indicates to Unprompted that we want to print this variable immediately for use in our prompt. Sometimes you don't want to do this, like when we set the CFG scale and Restore Faces earlier.

Now, inside of our web UI, we can change the prompt to this:

```
[override subject="panda"][file example]
```

That's it, now you've got pandas!

![image](https://user-images.githubusercontent.com/95403634/198938606-1ba13254-c7d7-44e8-8609-7e329686613d.png)

In the final section, we will learn about some more advanced functions.

</details>

<details><summary>Step 5: Conditional shortcodes</summary>

The last subject I want to discuss are the conditional shortcodes `[if]` and `[chance]`. These will evaluate given variable(s) in deciding what to output.

For our demo, we will run a check on the `subject` variable, and if it's set to `man`, we will make him wear a business suit 75% of the time. Here's how we can do this:

On a new line, we will write `wearing a business suit` inside of a conditional check...

```
[if subject="man"]wearing a business suit[/if]
```

> **💡 Tip:** Unprompted will automatically convert any linebreaks in our template to spaces, and it will also remove unnecessary/double spaces at the end of the processing chain.

Finally, if we want to make this occur only 75% of the time, we introduce `[chance]`:

```
[if subject="man"][chance 75]wearing a business suit[/chance][/if]
```

![image](https://user-images.githubusercontent.com/95403634/198940097-8102c57e-7b05-4aef-87e5-1c05606d73d9.png)

He'd like to congratulate you on making it this far.

</details>

<details><summary>GG no RE</summary>

I hope you found this starter guide useful and now have a better idea of what Unprompted brings to the table!

We have only scratched the surface here - when you're ready to do a deeper dive, please check out the full documentation here (or simply click on the Manual tab if you're inside of the app itself):

[Unprompted Manual](MANUAL.md)

Good luck!

</details>

</details>

<details><summary>Setting up Replacement Terms</summary>

Do you regularly use LORA files or other embeddings in your Stable Diffusion prompts? If so, you probably know that it can be a challenge to keep track of all the different filenames, trigger words, and optimal weights to use in your prompts.

You can solve this by setting up replacement terms with Unprompted.

Let's say you have the following prompt with a couple LORA tags:

```
an amazing illustration of pepe_frog<lora:pepeFrog_v20:0.8> bloodstainai<lora:bloodstainedVector_v10:0.75>
```

You can use the `[replace]` shortcode to perform find-and-replace operations on the inner content. So if we specify `[replace red=blue]`, then all instances of "red" will be swapped to "blue."

Here's where it gets interesting: **we can load our replacement strings from external files.**

## Dictionary setup

In your `unprompted` folder, create a subdirectory called `user` and make a file called `replacements.json` inside of that (i.e. `unprompted/user/replacements.json`).

Open `replacements.json` in your text editor of choice.

Let's write our new dictionary with "from":"to" replacement pairings:

```
{
	"from something":"to something else"
}
```

In place of `from something`, we want to insert an easy-to-remember shorthand for the complicated LORA tag.

Looking at the example prompt, we'll use `pepe the frog` for the first tag. Here is our updated dictionary:

```
{
	"pepe the frog":"pepe_frog<lora:pepeFrog_v20:0.8>"
}
```

Now, let's add a comma and a linebreak for the next entry.

We don't want to use `bloodstained` as our shorthand because it's too generic - sometimes you may want to include "bloodstained" in your prompts without invoking the LORA embedding. So we'll use `in the style of bloodstained` instead. We can also add an **alternative replacement** such as `bloodstained style` with a vertical pipe delimiter.

Here is our dictionary with both entries:

```
{
	"pepe the frog":"pepe_frog<lora:pepeFrog_v20:0.8>",
	"in the style of bloodstained|bloodstained style":"bloodstainai<lora:bloodstainedVector_v10:0.75>"
}
```

Save the file. To use it in your prompts, you must set it to the `_load` value of your `[replace]` block as shown below:

```
[replace _load="user/replacements.json"]an amazing illustration of pepe the frog in the style of bloodstained[/replace]
```

And you're done!

## How to automatically include [replace] in your prompts

If you're happy with your dictionary, you probably don't want to manually write `[replace]` all the time. Luckily, you don't have to.

Create or open a file called `config_user.json` in the root of `unprompted`.

Add an entry called `templates` as shown below:

```
{
	"templates":
	{
		"default":"[replace _load='user/replace.json']*[/replace]"
	}
}
```

The asterisk wildcard represents any prompt. Restart the WebUI and you're all set!

</details>