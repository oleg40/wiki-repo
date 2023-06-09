from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
import markdown2
import os
from random import randint

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):

    if util.get_entry(title):
        content = util.get_entry(title)
        if request.GET.get("edit") == "true":
            class EditForm(forms.Form):
                editText = forms.CharField(widget=forms.Textarea, label="Text")
            emptyForm = EditForm(initial={
                "editText": content
            })
            if request.method == "POST":
                filledForm = EditForm(request.POST)
                if filledForm.is_valid():
                    newText = filledForm.cleaned_data["editText"]
                    with open(f"entries/{title}.md", "w") as file:
                        file.write(newText)
                    return HttpResponseRedirect(title)
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "form": emptyForm
        })

        # if entry was found
        content = markdown2.markdown(content)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": content
        })
    
    # if entry was not found
    not_found = True
    return render(request, "encyclopedia/error.html", {
        "not_found": not_found
    })
   
def search(request):
    query = request.GET.get('q')
    if query:
        if util.get_entry(query):
            return HttpResponseRedirect(f"wiki/{query}")
        
        # if search field is not empty but there is no such page, find pages for which query is a substring
        filenames = util.list_entries()
        found = [filename for filename in filenames if filename.lower().find(query.lower()) != -1]
        return render(request, "encyclopedia/search.html", {
            "found": found
        })
    
    # if user submitted an empty search field
    return HttpResponseRedirect(reverse('index'))

def new(request):
    class NewEntryForm(forms.Form):
        title = forms.CharField(label="Title")
        text = forms.CharField(widget=forms.Textarea, label="Text")
    
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
            if title in util.list_entries():
                exists = True
                return render(request, "encyclopedia/error.html", {
                    "exists": exists,
                    "name": title
                })
            util.save_entry(title, text)
            return HttpResponseRedirect(f"wiki/{title}")

    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })

def random(request):
    entries = util.list_entries()
    idx = randint(0, (len(entries) - 1))
    return HttpResponseRedirect(f"../wiki/{entries[idx]}")