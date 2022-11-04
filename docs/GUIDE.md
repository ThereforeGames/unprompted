# Starter Guide

Let's walk through the process of making your own templates for Unprompted. It's fun and easy.

For the purposes of this guide, we will construct a basic "human generator" similar to the one that is included with the repo download.

## 1) Create the entry point

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

## 2) Using the \[choose\] shortcode

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

## 3) Managing Stable Diffusion options with \[set\]

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

## 4) Overriding parts of the template

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

## 5) Conditional shortcodes

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

## In conclusion

I hope you found this starter guide useful and now have a better idea of what Unprompted brings to the table!

We have only scratched the surface here - when you're ready to do a deeper dive, please check out the full documentation here:

[Unprompted Manual](MANUAL.md)

Good luck!