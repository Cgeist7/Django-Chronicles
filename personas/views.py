from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.template.response import TemplateResponse
from django.template.defaultfilters import slugify
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy, reverse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.contrib.auth import logout, login, authenticate
from django.db.models import F, Q
from django.db.models.base import ObjectDoesNotExist
from django.views.generic.edit import DeleteView, UpdateView, FormView, CreateView
from crispy_forms.layout import Submit, HTML
from crispy_forms.helper import FormHelper
from personas.models import Nation, Location, StoryObject, Relationship, Aspect, Ability, Story, MainMap, Chapter, Scene, Skill, Note, Communique, Equipment, GameStats, Place
from personas.models import Statistic, CombatInfo, GalleryImage, ScratchPad, Poster
from personas.forms import StoryObjectForm, NoteForm, CommuniqueForm, UserForm, UserProfileForm, SkillForm, AspectForm, AspectFormSetHelper, SkillFormSetHelper, AbilityForm, RelationshipForm
from personas.forms import StoryForm, ChapterForm, SceneForm, LocationForm, StatisticForm, CombatInfoForm, NationForm, ScratchPadForm, GalleryImageForm, MainMapForm, EquipmentForm
from personas.forms import BatchCommonStoryObjectForm, BatchStoryObjectForm, BatchFormSetHelper, create_relationship_form, RelationshipFormSetHelper, GameStatsForm, PlaceForm

from datetime import datetime
import network_personas


def return_object(s_object):
    # retrieve object type function

    if s_object.__class__.__name__ == 'StoryObject':
        so_type = "storyobject"
    elif s_object.__class__.__name__ == 'Location':
        so_type = "location"
    elif s_object.__class__.__name__ == 'Chapter':
        so_type = "chapter"
    elif s_object.__class__.__name__ == 'Scene':
        so_type = "scene"
    elif s_object.__class__.__name__ == 'Nation':
        so_type = "nation"
    else:
        so_type = "story"

    return so_type

# Permission functions


# Normal Views

def index(request):
    context_dict = {}

    try:
        stories = Story.objects.filter(published=True)

        context_dict['stories'] = stories
        context_dict['poster'] = Poster.objects.latest('publication_date')

    except Story.DoesNotExist:
        pass

    return render(request, 'personas/index.html', context_dict)


@login_required
def workshop(request, user):
    context_dict = {}

    user = request.user

    try:
        context_dict['user'] = user

        # Set up Stories
        context_dict['published_stories'] = Story.objects.filter(
            author=user).filter(published=True)

        context_dict['unpublished_stories'] = Story.objects.filter(
            author=user).filter(published=False)

        # Set up Chapters
        context_dict['published_chapters'] = Chapter.objects.filter(
            creator=user).filter(published=True).order_by("story", "number")

        context_dict['unpublished_chapters'] = Chapter.objects.filter(
            creator=user).filter(published=False).order_by("story", "number")

        # Set up Scenes
        context_dict['published_scenes'] = Scene.objects.filter(
            creator=user).filter(published=True).order_by("chapter__story", "chapter", "order")

        context_dict['unpublished_scenes'] = Scene.objects.filter(
            creator=user).filter(published=False).order_by("chapter__story", "chapter", "order")

        # Set up Nations
        context_dict['published_nations'] = Nation.objects.filter(
            creator=user).filter(published=True).order_by("story", "name")

        context_dict['unpublished_nations'] = Nation.objects.filter(
            creator=user).filter(published=False).order_by("story", "name")

        # Set up Locations
        context_dict['published_locations'] = Location.objects.filter(
            creator=user).filter(published=True).order_by("story", "name")

        context_dict['unpublished_locations'] = Location.objects.filter(
            creator=user).filter(published=False).order_by("story", "name")

        # Set up Organizations
        context_dict['published_organizations'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Organization").filter(
            published=True).order_by("story", "name")

        context_dict['unpublished_organizations'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Organization").filter(
            published=False).order_by("story", "name")

        # Set up Forces
        context_dict['published_forces'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Force").filter(
            published=True).order_by("story", "name")

        context_dict['unpublished_forces'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Force").filter(
            published=False).order_by("story", "name")

        # Set up Characters
        context_dict['published_characters'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Character").filter(
            published=True).order_by("story", "name")

        context_dict['unpublished_characters'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Character").filter(
            published=False).order_by("story", "name")

        # Set up Creatures
        context_dict['published_creatures'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Creature").filter(
            published=True).order_by("story", "name")

        context_dict['unpublished_creatures'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Creature").filter(
            published=False).order_by("story", "name")

        # Set up Things
        context_dict['published_things'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Thing").filter(
            published=True).order_by("story", "name")

        context_dict['unpublished_things'] = StoryObject.objects.filter(
            creator=user).filter(c_type="Thing").filter(
            published=False).order_by("story", "name")

    except Story.DoesNotExist:
        pass

    return render(request, 'personas/workshop.html', context_dict)


def collections(request):
    storyobject_list = StoryObject.objects.all()
    location_list = Location.objects.all()
    organization_list = StoryObject.objects.filter(
        c_type="Organization").distinct().order_by('name')

    context_dict = {'boldmessage': "Personas", 'storyobjects': storyobject_list,
        'locations': location_list, 'organizations': organization_list}

    return render(request, 'personas/collections.html', context_dict)


def about(request):
    context_dict = {}
    return render(request, 'personas/about.html', context_dict)


def location(request, location_name_slug):

    context_dict = {}

    try:
        location = Place.objects.get(slug=location_name_slug)
        story = location.story

        context_dict['story'] = Story.objects.get(location=location)

        context_dict['location'] = location
        context_dict['location_name'] = location.name
        context_dict['creator'] = location.creator
        context_dict['image'] = location.image
        context_dict['terrain'] = location.terrain
        context_dict['features'] = location.features
        context_dict['description'] = location.description
        context_dict['nation'] = location.nation
        context_dict['latitude'] = location.latitude
        context_dict['longitude'] = location.longitude
        context_dict['slug'] = location.slug
        context_dict['scenes'] = Scene.objects.filter(
            location__name=location.name).filter(published=True).order_by("order")
        context_dict['organizations'] = StoryObject.objects.filter(
                base_of_operations=location).filter(c_type="Organization").filter(published=True).distinct().order_by('name')
        context_dict['storyobjects'] = StoryObject.objects.filter(
            base_of_operations__name=location.name).filter(published=True).filter(~Q(c_type="Organization"))

        context_dict['notes'] = Note.objects.filter(location__name=location.name)

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                form.save(location=location, creator=request.user, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Location.DoesNotExist:
        pass

    return render(request, 'personas/location.html', context_dict)


def scene(request, scene_name_slug):

    context_dict = {}

    try:
        scene = Scene.objects.get(slug=scene_name_slug)

        context_dict['scene'] = scene
        context_dict['scene_title'] = scene.title
        context_dict['slug'] = scene_name_slug
        context_dict['location'] = scene.location
        context_dict['purpose'] = scene.purpose
        context_dict['resolution'] = scene.resolution
        context_dict['description'] = scene.description
        context_dict['publication_date'] = scene.publication_date
        context_dict['storyobjects'] = StoryObject.objects.filter(scene__title=scene.title).filter(published=True)

        context_dict['story'] = Story.objects.get(chapter__scene__title=scene.title)
        context_dict['chapter'] = Chapter.objects.get(scene__title=scene.title)

        context_dict['notes'] = Note.objects.filter(
            scene__title=scene.title)[0:10]

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                post_scene = scene
                post_creator = request.user
                form.save(scene=post_scene, creator=post_creator, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Scene.DoesNotExist:
        pass

    return render(request, 'personas/scene.html', context_dict)


def nation(request, nation_name_slug):

    context_dict = {}

    try:
        nation = Nation.objects.get(slug=nation_name_slug)
        story = Story.objects.get(nation=nation)

        context_dict['nation'] = nation
        context_dict['story'] = story
        context_dict['places'] = Place.objects.filter(
            nationality=nation).filter(published=True).distinct()

        context_dict['notes'] = Note.objects.filter(
            nation__name=nation.name)[0:10]

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                post_nation = nation
                post_creator = request.user
                form.save(nation=post_nation, creator=post_creator, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Nation.DoesNotExist:
        pass

    return render(request, 'personas/nation.html', context_dict)


def place(request, place_name_slug):

    context_dict = {}

    try:
        storyobject = Place.objects.get(slug=place_name_slug)

        context_dict['name'] = storyobject.name
        context_dict['storyobject'] = storyobject
        context_dict['creator'] = storyobject.creator
        context_dict['story'] = storyobject.story
        context_dict['role'] = storyobject.role
        context_dict['c_type'] = storyobject.c_type
        context_dict['description'] = storyobject.description

        # Get Latitude & Longitud
        context_dict['latitude'] = storyobject.latitude
        context_dict['longitude'] = storyobject.longitude

        # Return JSON object for relationship map

        associated_places = Relationship.objects.filter(
            (Q(from_storyobject__name=storyobject.name) &
            Q(to_storyobject__c_type="Place")) |
            (Q(to_storyobject__name=storyobject.name) &
                Q(from_storyobject__c_type="Place"))
            ).order_by('-weight')

        story_objects = {}

        story_objects[storyobject] = storyobject

        for rel in associated_places:
            story_objects[rel.to_storyobject] = rel.to_storyobject
            story_objects[rel.from_storyobject] = rel.from_storyobject

        context_dict['associated_places'] = associated_places
        context_dict['result'] = network_personas.return_json_graph(
            story_objects)

        # Game statistics
        try:
            context_dict['gamestats'] = GameStats.objects.get(
                storyobject__name=storyobject.name)
        except GameStats.DoesNotExist:
            context_dict['gamestats'] = None

        context_dict['aspects'] = Aspect.objects.filter(
            storyobject__name=storyobject.name)

        context_dict['associated_storyobjects'] = Relationship.objects.filter(
            Q(to_storyobject__name=storyobject.name) &
                ~Q(from_storyobject__c_type="Place")).order_by('-weight')

        context_dict['notes'] = Note.objects.filter(
            storyobject__name=storyobject.name)

        context_dict['gallery_images'] = GalleryImage.objects.filter(
            storyobject=storyobject)

        context_dict['nationality'] = storyobject.nationality

        context_dict['gamestats_toggle'] = storyobject.gamestats_toggle
        context_dict['gallery_toggle'] = storyobject.gallery_toggle

        # Note Form Section
        noteform = NoteForm(request.POST, prefix="note")

        if request.method == 'POST':

            if 'save' in request.POST:
                creator = request.user
                note_subject = storyobject

                noteform = NoteForm(request.POST)

                if noteform.is_valid():
                    noteform.save(
                        creator=creator, storyobject=note_subject, commit=True)

                    return HttpResponseRedirect("/personas/place/{}/#notes".format(storyobject_name_slug))

                else:
                    print (context_dict['noteform'].errors)

        else:

            context_dict['noteform'] = NoteForm()

    except storyobject.DoesNotExist:
        pass

    return render(request, 'personas/place.html', context_dict)


def storyobject(request, storyobject_name_slug):

    context_dict = {}

    try:
        storyobject = StoryObject.objects.get(slug=storyobject_name_slug)

        context_dict['storyobject_name'] = storyobject.name
        context_dict['storyobject'] = storyobject
        context_dict['creator'] = storyobject.creator
        context_dict['story'] = storyobject.story
        context_dict['role'] = storyobject.role
        context_dict['c_type'] = storyobject.c_type
        context_dict['description'] = storyobject.description

        # Get Latitude & Longitud

        # Return JSON object for relationship map

        story_objects = {}

        neighbours = Relationship.objects.filter(
                    Q(from_storyobject__name=storyobject.name) |
                    Q(to_storyobject__name=storyobject.name))

        story_objects[storyobject] = storyobject

        for rel in neighbours:
            story_objects[rel.to_storyobject] = rel.to_storyobject
            story_objects[rel.from_storyobject] = rel.from_storyobject


        context_dict['result'] = network_personas.return_json_graph(
            story_objects)

        # Game statistics
        try:
            context_dict['gamestats'] = GameStats.objects.get(
                storyobject__name=storyobject.name)
        except GameStats.DoesNotExist:
            context_dict['gamestats'] = None

        # Set up ScratchPad and Equipment for storyobject

        try:
            scratchpad = ScratchPad.objects.get(
                storyobject__name=storyobject.name)
        except ScratchPad.DoesNotExist:
            scratchpad = ScratchPad(storyobject=storyobject, creator=storyobject.creator,
                content="Enter info here and save to update", date=datetime.now())

        context_dict['scratchpad'] = scratchpad

        try:
            equipment = Equipment.objects.get(
                storyobject__name=storyobject.name)
        except Equipment.DoesNotExist:
            equipment = Equipment(storyobject=storyobject, creator=storyobject.creator,
                date=datetime.now())

        context_dict['equipment'] = equipment

        context_dict['aspects'] = Aspect.objects.filter(
            storyobject__name=storyobject.name)

        context_dict['type_1_statistics'] = Statistic.objects.filter(
            storyobject__name=storyobject.name).filter(stat_type="Type_1").order_by(
            'name')
        context_dict['type_2_statistics'] = Statistic.objects.filter(
            storyobject__name=storyobject.name).filter(stat_type="Type_2").order_by(
            'name')
        context_dict['type_3_statistics'] = Statistic.objects.filter(
            storyobject__name=storyobject.name).filter(stat_type="Type_3").order_by(
            'name')
        context_dict['type_4_statistics'] = Statistic.objects.filter(
            storyobject__name=storyobject.name).filter(stat_type="Type_4").order_by(
            'name')

        context_dict['type_1_skills'] = Skill.objects.filter(
            storyobject__name=storyobject.name).filter(s_type="Type_1").order_by(
            'name')
        context_dict['type_2_skills'] = Skill.objects.filter(
            storyobject__name=storyobject.name).filter(s_type="Type_2").order_by(
            'name')
        context_dict['type_3_skills'] = Skill.objects.filter(
            storyobject__name=storyobject.name).filter(s_type="Type_3").order_by(
            'name')
        context_dict['type_4_skills'] = Skill.objects.filter(
            storyobject__name=storyobject.name).filter(s_type="Type_4").order_by(
            'name')

        context_dict['combat_info'] = CombatInfo.objects.filter(
            storyobject__name=storyobject.name)

        context_dict['my_relationships'] = Relationship.objects.filter(
            Q(from_storyobject__name=storyobject.name) &
            (~Q(to_storyobject__c_type="Organization") &
                ~Q(to_storyobject__c_type="Place"))).order_by('-weight')

        context_dict['other_relationships'] = Relationship.objects.filter(
            Q(to_storyobject__name=storyobject.name) &
            (~Q(from_storyobject__c_type="Organization") &
                ~Q(from_storyobject__c_type="Place"))).order_by('-weight')

        context_dict['abilities'] = Ability.objects.filter(
            storyobject__name=storyobject.name)

        context_dict['notes'] = Note.objects.filter(
            storyobject__name=storyobject.name)

        context_dict['gallery_images'] = GalleryImage.objects.filter(
            storyobject=storyobject)

        context_dict['communiques'] = Communique.objects.filter(
            Q(author__name=storyobject.name) |
            Q(receiver__name=storyobject.name))

        context_dict['nationality'] = storyobject.nationality

        context_dict['places'] = Relationship.objects.filter(
            (Q(from_storyobject__name=storyobject.name) &
            Q(to_storyobject__c_type="Place"))
            ).order_by('-weight')

        context_dict['my_memberships'] = Relationship.objects.filter(
            Q(from_storyobject__name=storyobject.name) &
            (Q(from_storyobject__c_type="Organization") |
            Q(to_storyobject__c_type="Organization"))).order_by('-weight')

        context_dict['other_memberships'] = Relationship.objects.filter(
            Q(to_storyobject__name=storyobject.name) &
            (Q(from_storyobject__c_type="Organization") |
            Q(to_storyobject__c_type="Organization"))).order_by('-weight')

        # Membership.objects.filter(storyobject=storyobject)

        context_dict['gamestats_toggle'] = storyobject.gamestats_toggle
        context_dict['stats_toggle'] = storyobject.stats_toggle
        context_dict['skill_toggle'] = storyobject.skill_toggle
        context_dict['combat_toggle'] = storyobject.combat_toggle
        context_dict['equipment_toggle'] = storyobject.equipment_toggle
        context_dict['gallery_toggle'] = storyobject.gallery_toggle
        context_dict['social_toggle'] = storyobject.social_toggle

        # Note Form Section
        noteform = NoteForm(request.POST, prefix="note")
        communique_form = CommuniqueForm(request.POST, prefix="comm")

        if request.method == 'POST':

            if 'save' in request.POST:
                creator = request.user
                note_subject = storyobject

                noteform = NoteForm(request.POST)

                if noteform.is_valid():
                    noteform.save(
                        creator=creator, storyobject=note_subject, commit=True)

                    return HttpResponseRedirect("/personas/storyobject/{}/#notes".format(storyobject_name_slug))

                else:
                    print (context_dict['noteform'].errors)

            elif 'send' in request.POST:
                post_creator = storyobject

                communique_form = CommuniqueForm(request.POST)

                if request.user == storyobject.creator:

                    if communique_form.is_valid():
                        communique_form.save(author=post_creator, commit=True)

                        return HttpResponseRedirect("/personas/storyobject/{}/#social".format(storyobject_name_slug))

                    else:
                        print (context_dict['communique_form'].errors)

                else:
                    print("You do not have permission to send a communique from this storyobject.")
                    return HttpResponseRedirect("/personas/storyobject/{}/#social".format(storyobject_name_slug))

            if 'snapshot' in request.POST:

                scratchpadform = ScratchPadForm(request.POST or None, instance=scratchpad)

                if scratchpadform.is_valid():
                    scratchpadform.storyobject = storyobject

                    scratchpadform.save()

                    context_dict['scratchpadform'] = ScratchPadForm(instance=scratchpad)

                    return HttpResponseRedirect("/personas/storyobject/{}/#combat".format(storyobject_name_slug))

                else:
                    print (context_dict['scratchpadform'].errors)

            if 'record' in request.POST:

                equipmentform = EquipmentForm(request.POST or None, instance=equipment)

                if equipmentform.is_valid():
                    equipmentform.storyobject = storyobject

                    equipmentform.save()

                    context_dict['equipmentform'] = EquipmentForm(instance=equipment)

                    return HttpResponseRedirect("/personas/storyobject/{}/#equipment".format(storyobject_name_slug))

                else:
                    print (context_dict['equipmentform'].errors)

        else:

            context_dict['noteform'] = NoteForm()
            context_dict['communique_form'] = CommuniqueForm(story=storyobject.story)
            context_dict['scratchpadform'] = ScratchPadForm(instance=scratchpad)
            context_dict['equipmentform'] = EquipmentForm(instance=equipment)


    except storyobject.DoesNotExist:
        pass

    return render(request, 'personas/storyobject.html', context_dict)


def chapter(request, chapter_name_slug):

    context_dict = {}

    try:
        chapter = Chapter.objects.get(slug=chapter_name_slug)
        scenes = Scene.objects.filter(chapter__title=chapter.title).filter(
            published=True).order_by('order')

        context_dict['chapter_title'] = chapter.title
        context_dict['chapter'] = chapter
        context_dict['slug'] = chapter_name_slug
        context_dict['story'] = chapter.story
        context_dict['description'] = chapter.description

        context_dict['scenes'] = scenes

        context_dict['storyobjects'] = StoryObject.objects.filter(
            scene__chapter__title=chapter.title).filter(published=True).distinct()
        context_dict['locations'] = Location.objects.filter(
            scene__chapter__title=chapter.title).filter(published=True).distinct()


        context_dict['notes'] = Note.objects.filter(
            chapter__title=chapter.title)[0:10]

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                post_chapter = chapter
                post_creator = request.user
                form.save(chapter=post_chapter, creator=post_creator, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Chapter.DoesNotExist:
        pass

    return render(request, 'personas/chapter.html', context_dict)


def story(request, story_name_slug):

    context_dict = {}

    try:
        story = Story.objects.get(slug=story_name_slug)
        chapters = Chapter.objects.filter(story__title=story.title).filter(
            published=True).order_by("number")

        context_dict['chapters'] = chapters

        context_dict['story'] = story
        context_dict['author'] = story.author
        context_dict['setting'] = story.setting
        context_dict['themes'] = story.themes
        context_dict['publication_date'] = story.publication_date
        context_dict['image'] = story.image
        context_dict['genre'] = story.genre
        #context_dict['artifacts'] = Item.objects.filter(story=story).distinct()

        mainmaps = MainMap.objects.filter(
            story__title=story.title)
        context_dict['mainmaps'] = mainmaps

        context_dict['description'] = story.description

        context_dict['notes'] = Note.objects.filter(
            story__title=story.title)

        scenes = Scene.objects.filter(
            chapter__story__title=story.title).filter(
            published=True).distinct().order_by("order")

        context_dict['scenes'] = scenes

        context_dict['characters'] = StoryObject.objects.filter(
                story=story).filter(
                published=True).filter(
                c_type="Character").distinct().order_by('name')

        context_dict['artifacts'] = StoryObject.objects.filter(
                story=story).filter(
                published=True).filter(
                c_type="Thing").distinct().order_by('name')

        context_dict['creatures'] = StoryObject.objects.filter(
                story=story).filter(
                published=True).filter(
                c_type="Creature").distinct().order_by('name')

        context_dict['forces'] = StoryObject.objects.filter(
                story=story).filter(
                published=True).filter(
                c_type="Force").distinct().order_by('name')

        context_dict['locations'] = StoryObject.objects.filter(
                story=story).filter(
                published=True).filter(
                c_type="Place").distinct().order_by('name')

        context_dict['organizations'] = StoryObject.objects.filter(
            story=story).filter(
            published=True).filter(
            c_type="Organization").distinct().order_by('name')

        context_dict['nations'] = Nation.objects.filter(
            story=story).filter(
            published=True).distinct().order_by('name')

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                post_story = story
                post_creator = request.user
                form.save(story=post_story, creator=post_creator, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Story.DoesNotExist:
        pass

    return render(request, 'personas/story.html', context_dict)


def note(request, story_slug, pk):

    context_dict = {}
    context_dict['story'] = get_object_or_404(Story, slug=story_slug)
    note = get_object_or_404(Note, pk=pk)

    context_dict['note'] = note

    return render(request, 'personas/note.html', context_dict)


def mainmap(request, mainmap_slug):
    context_dict = {}

    mainmap = MainMap.objects.get(slug=mainmap_slug)

    try:
        context_dict['map_name'] = mainmap.name
        context_dict['story'] = mainmap.story
        context_dict['base_latitude'] = mainmap.base_latitude
        context_dict['base_longitude'] = mainmap.base_longitude
        context_dict['tile'] = mainmap.tiles

        context_dict['locations'] = Location.objects.filter(
            story=mainmap.story).distinct()

    except MainMap.DoesNotExist:
        pass

    return render(request, 'personas/mainmap.html', context_dict)


def relationship_map(request, slug):

    story_objects = {}

    try:
        storyobject = StoryObject.objects.get(slug=slug)
        title = storyobject.name
        story = storyobject.story

        neighbours = Relationship.objects.filter(
                    Q(from_storyobject__name=storyobject.name) |
                    Q(to_storyobject__name=storyobject.name))

        story_objects[storyobject] = storyobject

        for rel in neighbours:
            story_objects[rel.to_storyobject] = rel.to_storyobject
            story_objects[rel.from_storyobject] = rel.from_storyobject

    except ObjectDoesNotExist:
        story = Story.objects.get(slug=slug)
        title = story.title
        story_objects = StoryObject.objects.filter(story=story)

    result = network_personas.return_json_graph(story_objects)

    return render(request, 'personas/relationship_map.html', {
        'slug': slug, 'title': title, 'story':story, 'result':result})


# Admin Views

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            #profile = profile_form.save(commit=False)
            #profile.user = request.user

            #if 'image' in request.FILES:
            #    profile.image = request.FILES['image']

            #profile.save()

            registered = True

            send_mail("Personas: Account Activated",
                '''Welcome to Personas.\n\n
                Your account has been activated as: {}\n\n
                http:story-chronicles.herokuapp.com/personas/'''.format(
                    user.username),
                "personas.story@gmail.com",
                [user.email, "personas.story@gmail.com"])

            return index(request)

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'personas/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 
        'registered': registered})


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:

                login(request, user)
                return HttpResponseRedirect('/personas/')
            else:
                return HttpResponse("Your Personas account is disabled.")

        else:
            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'personas/login.html', {})


@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/personas/')


# Add content Views

@login_required
def add_storyobject(request, story_title_slug, c_type):

    story = Story.objects.get(slug=story_title_slug)

    if request.method == 'POST':
        storyobject_form = StoryObjectForm(request.POST, request.FILES)

        creator = request.user

        if storyobject_form.is_valid():
            slug = slugify("{}-{}".format(
                story.title, storyobject_form.cleaned_data['name']))

            storyobject_form.save(creator=creator, story=story,
                commit=True)

            return HttpResponseRedirect("/personas/storyobject/{}".format(slug))

        else:
            print (storyobject_form.errors)

    else:

        storyobject_form = StoryObjectForm(story=story)

    return render(request, 'personas/add_storyobject.html',
        {'storyobject_form': storyobject_form, 'story':story, "c_type":c_type})


@login_required
def add_place(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)

    mainmap = MainMap.objects.filter(story=story).first()

    if mainmap:
        pass
    else:
        mainmap = MainMap(base_latitude=50.000, base_longitude=-1.3,
            story=story,
            tiles="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")

    c_type = 'Place'

    if request.method == 'POST':
        place_form = PlaceForm(request.POST, request.FILES)

        creator = request.user

        if place_form.is_valid():
            slug = slugify("{}-{}".format(
                story.title, place_form.cleaned_data['name']))

            place_form.save(creator=creator, story=story,
                commit=True)

            return HttpResponseRedirect("/personas/place/{}".format(slug))

        else:
            print (place_form.errors)

    else:

        place_form = PlaceForm(story=story)

    return render(request, 'personas/add_place.html',
        {'place_form': place_form, 'story':story, "c_type":c_type,
        'mainmap': mainmap})


@login_required
def add_batch_storyobject(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)

    StoryObjectFormSet = modelformset_factory(StoryObject,
        form=BatchStoryObjectForm, extra=8)

    if request.method == 'POST':

        formset = StoryObjectFormSet(request.POST, request.FILES, prefix="batch")
        helper = BatchFormSetHelper()
        common_form = BatchCommonStoryObjectForm(request.POST, prefix="common")

        creator = request.user

        if formset.is_valid() and common_form.is_valid():
            for form in formset:
                so = StoryObject()
                try:
                    so.name = form.cleaned_data['name']
                    so.story = story
                    so.creator = creator
                    so.role = form.cleaned_data['role']
                    so.c_type = form.cleaned_data['c_type']
                    so.description = form.cleaned_data['description']
                    so.image = form.cleaned_data['image']

                    if common_form.cleaned_data['gamestats_toggle']:
                        so.gamestats_toggle = True
                    else:
                        so.gamestats_toggle = False

                    if common_form.cleaned_data['stats_toggle']:
                        so.stats_toggle = True
                    else:
                        so.stats_toggle = False

                    if common_form.cleaned_data['skill_toggle']:
                        so.skill_toggle = True
                    else:
                        so.skill_toggle = False

                    if common_form.cleaned_data['combat_toggle']:
                        so.combat_toggle = True
                    else:
                        so.combat_toggle = False

                    if common_form.cleaned_data['equipment_toggle']:
                        so.equipment_toggle = True
                    else:
                        so.equipment_toggle = False

                    if common_form.cleaned_data['gallery_toggle']:
                        so.gallery_toggle = True
                    else:
                        so.gallery_toggle = False

                    if common_form.cleaned_data['social_toggle']:
                        so.social_toggle = True
                    else:
                        so.social_toggle = False

                    if common_form.cleaned_data['published']:
                        so.published = True
                    else:
                        so.published = False

                    so.slug = slugify("{}-{}".format(
                        story.title, form.cleaned_data['name']))

                    so.save()

                except KeyError as e:
                    pass

            return HttpResponseRedirect("/personas/story/{}#story_objects".format(story.slug))

        else:
            print (formset.errors, common_form.errors)

    else:

        formset = StoryObjectFormSet(prefix="batch",
            queryset=Relationship.objects.none())
        helper = BatchFormSetHelper()
        common_form = BatchCommonStoryObjectForm(prefix="common")

    return render(request, 'personas/add_batch_storyobject.html',
        {'formset': formset, 'common_form': common_form, 'helper': helper, 'story':story})


@login_required
def add_batch_relationship(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)
    user = request.user

    BatchRelationshipForm = create_relationship_form(story, user)
    RelationshipFormSet = modelformset_factory(model=Relationship,
        form=BatchRelationshipForm, extra=10)

    if request.method == 'POST':

        formset = RelationshipFormSet(request.POST)
        helper = RelationshipFormSetHelper()

        if formset.is_valid():
            formset.save()

            return HttpResponseRedirect("/personas/story/{}".format(story.slug))

        else:
            print (formset.errors)

    else:

        formset = RelationshipFormSet(queryset=Relationship.objects.none())
        helper = RelationshipFormSetHelper()

    return render(request, 'personas/add_batch_relationship.html',
        {'formset': formset, 'helper':helper,'story':story})



@login_required
def create_story(request):

    if request.method == 'POST':
        story_form = StoryForm(request.POST, request.FILES)

        creator = request.user

        if story_form.is_valid():
            slug = slugify(story_form.cleaned_data['title'])

            story_form.save(author=creator, commit=True)

            return HttpResponseRedirect("/personas/story/{}".format(slug))

        else:
            print (story_form.errors)

    else:

        story_form = StoryForm()

    return render(request, 'personas/create_story.html',
        {'story_form': story_form})


@login_required
def add_aspect(request, storyobject_name_slug):

    aspects = Aspect.objects.filter(storyobject__slug=storyobject_name_slug)

    storyobject = StoryObject.objects.get(slug=storyobject_name_slug)
    story = storyobject.story

    if request.method == 'POST':

        form = AspectForm(request.POST)

        if form.is_valid():
            aspect_storyobject = storyobject

            #for f in formset:
            cd = form.cleaned_data
            if not cd.get('name'):
                pass
            else:
                name = cd.get('name')
                label = cd.get('label')
                aspect = Aspect(
                    name=name, label=label,
                    storyobject=aspect_storyobject)

                aspect.save()
                form = AspectForm()

            return HttpResponseRedirect("")

        else:
            print (form.errors)

    else:

        form = AspectForm()

    return render(request, 'personas/add_aspect.html', {'form': form,
        'slug': storyobject_name_slug, 'storyobject': storyobject,
        'aspects': aspects, 'story':story})


@login_required
def add_skills(request, storyobject_name_slug):

    #SkillFormSet = formset_factory(SkillForm, extra=10, max_num=10)
    #helper = SkillFormSetHelper()

    skills = Skill.objects.filter(storyobject__slug=storyobject_name_slug)

    storyobject = StoryObject.objects.get(slug=storyobject_name_slug)

    story = storyobject.story

    type_1_skills = Skill.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(s_type="Type_1")
    type_2_skills = Skill.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(s_type="Type_2")
    type_3_skills = Skill.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(s_type="Type_3")
    type_4_skills = Skill.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(s_type="Type_4")

    if request.method == 'POST':

        form = SkillForm(request.POST or None, storyobject=storyobject)

        if form.is_valid():
            skill_storyobject = storyobject

            #for f in formset:
            cd = form.cleaned_data
            if cd.get('name') == None:
                pass
            else:
                name = cd.get('name')
                value = cd.get('value')
                s_type = cd.get('s_type')
                skill = Skill(
                    name=name, value=value, storyobject=skill_storyobject, s_type=s_type)

                skill.save()
                form = SkillForm(storyobject=storyobject)

            HttpResponseRedirect("")

        else:
            print (form.errors)

    else:
        form = SkillForm(storyobject=storyobject)

        #helper = SkillFormSetHelper()
        #helper.add_input(Submit("submit", "Save"))
        #helper.add_input(Submit("cancel", "Cancel"))

    return render(request, 'personas/add_skills.html', {'form': form,
        'slug': storyobject_name_slug, 'storyobject': storyobject,
        'type_1_skills': type_1_skills, 'type_2_skills': type_2_skills,
        'type_3_skills': type_3_skills, 'type_4_skills': type_4_skills,
        'story':story})


@login_required
def add_statistics(request, storyobject_name_slug):

    #StatisticFormSet = formset_factory(StatisticForm, extra=10, max_num=10)
    #helper = StatisticFormSetHelper()

    statistics = Statistic.objects.filter(storyobject__slug=storyobject_name_slug)

    storyobject = StoryObject.objects.get(slug=storyobject_name_slug)

    story = storyobject.story

    type_1_statistics = Statistic.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(stat_type="Type_1")
    type_2_statistics = Statistic.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(stat_type="Type_2")
    type_3_statistics = Statistic.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(stat_type="Type_3")
    type_4_statistics = Statistic.objects.filter(
            storyobject__slug=storyobject_name_slug).filter(stat_type="Type_4")

    if request.method == 'POST':

        form = StatisticForm(request.POST or None, storyobject=storyobject)

        if form.is_valid():
            statistic_storyobject = storyobject

            #for f in formset:
            cd = form.cleaned_data
            if cd.get('name') == None:
                pass
            else:
                name = cd.get('name')
                value = cd.get('value')
                s_type = cd.get('stat_type')
                statistic = Statistic(
                    name=name, value=value, storyobject=statistic_storyobject, stat_type=s_type)

                statistic.save()
                form = StatisticForm(storyobject=storyobject)

            HttpResponseRedirect("")

        else:
            print (form.errors)

    else:
        form = StatisticForm(storyobject=storyobject)

    return render(request, 'personas/add_statistics.html', {'form': form,
        'slug': storyobject_name_slug, 'storyobject': storyobject,
        'type_1_statistics': type_1_statistics, 'type_2_statistics': type_2_statistics,
        'type_3_statistics': type_3_statistics, 'type_4_statistics': type_4_statistics,
        'story':story})


@login_required
def add_combat_info(request, storyobject_name_slug):

    combat_info_list = CombatInfo.objects.filter(storyobject__slug=storyobject_name_slug)

    storyobject = StoryObject.objects.get(slug=storyobject_name_slug)

    story = storyobject.story

    if request.method == 'POST':

        form = CombatInfoForm(request.POST or None)

        if form.is_valid():
            combat_info_storyobject = storyobject

            cd = form.cleaned_data
            if cd.get('title') == None:
                pass
            else:
                title = cd.get('title')
                data = cd.get('data')
                combat_info = CombatInfo(
                    title=title, data=data, storyobject=combat_info_storyobject)

                combat_info.save()
                form = CombatInfoForm()

            HttpResponseRedirect("")

        else:
            print (form.errors)

    else:
        form = CombatInfoForm()

    return render(request, 'personas/add_combat_info.html', {'form': form,
        'slug': storyobject_name_slug, 'storyobject': storyobject, 'story':story,
        'combat_info':combat_info_list})


@login_required
def add_ability(request, storyobject_name_slug):

    abilities = Ability.objects.filter(storyobject__slug=storyobject_name_slug)

    storyobject = StoryObject.objects.get(slug=storyobject_name_slug)
    story = storyobject.story

    if request.method == 'POST':

        ability_form = AbilityForm(request.POST)

        if ability_form.is_valid():

            ability_data = ability_form.cleaned_data

            if ability_data.get('name') == None:
                pass
            else:
                name = ability_data.get('name')
                description = ability_data.get('description')
                ability = Ability(
                    name=name, description=description, storyobject=storyobject)

                ability.save()
                ability_form = AbilityForm()

            HttpResponseRedirect("")

        else:
            print (ability_form.errors)

    else:
        ability_form = AbilityForm()

    return render(request, 'personas/add_ability.html', {
        'slug': storyobject_name_slug, 'storyobject': storyobject,
        'abilities': abilities, 'story':story,
        'ability_form':ability_form})


@login_required
def add_gamestats(request, storyobject_name_slug):

    storyobject = StoryObject.objects.get(slug=storyobject_name_slug)
    story = storyobject.story

    if request.method == 'POST':

        form = GameStatsForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            content = form_data.get('content')

            gamestats = GameStats(storyobject=storyobject,
                content=content)

            gamestats.save()

            return HttpResponseRedirect("/personas/storyobject/{}".format(
                storyobject.slug))

        else:
            print (gamestats_form.errors)

    else:
        form = GameStatsForm()

    return render(request, 'personas/add_gamestats.html', {
        'slug': storyobject_name_slug, 'storyobject': storyobject,
        'story':story, 'form':form})


@login_required
def add_relationships(request, storyobject_name_slug):

    storyobject = StoryObject.objects.get(slug=storyobject_name_slug)

    relationships = Relationship.objects.filter(Q(to_storyobject=storyobject) |
        Q(from_storyobject=storyobject))

    story = storyobject.story
    data = {"from_storyobject": storyobject}

    if request.method == 'POST':

        relationship_form = RelationshipForm(request.POST or None)

        if relationship_form.is_valid():

            relationship_data = relationship_form.cleaned_data

            if relationship_data.get('to_storyobject') == None:
                pass
            else:
                to_storyobject = relationship_data.get('to_storyobject')
                relationship_description = relationship_data.get('relationship_description')
                weight = relationship_data.get('weight')
                relationship_class = relationship_data.get('relationship_class')
                relationship = Relationship(
                    from_storyobject=storyobject,
                    to_storyobject=to_storyobject,
                    relationship_description=relationship_description,
                    relationship_class=relationship_class, weight=weight)

                relationship.save()
                relationship_form = RelationshipForm(story=story)

            HttpResponseRedirect("")

        else:
            print (relationship_form.errors)

    else:
        relationship_form = RelationshipForm(story=story)

    return render(request, 'personas/add_relationships.html', {
        'slug': storyobject_name_slug, 'storyobject': storyobject, 'story':story,
        'relationships': relationships, 'relationship_form':relationship_form})


@login_required
def add_chapter(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)

    chapters = Chapter.objects.filter(story__slug=story_title_slug).order_by("-number")

    storyobjects = StoryObject.objects.filter(story=story)

    if request.method == 'POST':

        chapter_form = ChapterForm(request.POST or None)

        if chapter_form.is_valid():

            chapter_data = chapter_form.cleaned_data

            if chapter_data.get('title') == None:
                pass
            else:
                title = chapter_data.get('title')
                number = chapter_data.get('number')
                chapter_description = chapter_data.get('description')
                chapter_slug = slugify("{}-{}".format(story.title,
                    chapter_data.get('title')))
                chapter = Chapter(title=title, story=story, number=number,
                    description=chapter_description, slug=chapter_slug,
                    creator=request.user)

                chapter.save()
                chapter_form = ChapterForm()

            return HttpResponseRedirect("/personas/chapter/{}".format(chapter_slug))

        else:
            print (chapter_form.errors)

    else:
        chapter_form = ChapterForm()

    return render(request, 'personas/add_chapter.html', {
        'slug': story_title_slug, 'story':story,
        'chapters': chapters, 'chapter_form':chapter_form})


@login_required
def add_scene(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)

    scenes = Scene.objects.filter(chapter__story__slug=story_title_slug).order_by("-number")

    storyobjects = StoryObject.objects.filter(story=story)

    if request.method == 'POST':

        scene_form = SceneForm(request.POST or None)

        if scene_form.is_valid():
            scene = scene_form.save(commit=False)
            scene.slug = slugify("{}-{}".format(story.title, scene.title))
            scene.creator = request.user
            scene.save()
            scene_form.save_m2m()

            return HttpResponseRedirect("/personas/scene/{}".format(scene.slug))

        else:
            print (scene_form.errors)

    else:
        scene_form = SceneForm(story=story)

    return render(request, 'personas/add_scene.html', {
        'slug': story_title_slug, 'story':story, 'scenes': scenes,
        'scene_form':scene_form, 'storyobjects':storyobjects})


@login_required
def add_location(request, story_title_slug):


    story = Story.objects.get(slug=story_title_slug)

    mainmap = MainMap.objects.filter(story=story).first()

    if mainmap:
        pass
    else:
        mainmap = MainMap(base_latitude=50.000, base_longitude=-1.3,
            story=story,
            tiles="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")


    locations = Location.objects.filter(story__slug=story_title_slug)

    if request.method == 'POST':

        location_form = LocationForm(request.POST, request.FILES)

        if location_form.is_valid():
            location = location_form.save(commit=False)
            location.creator = request.user
            location.story = story
            location.slug = slugify("{}-{}".format(story.title, location.name))
            location.save()
            #location_form.save_m2m()

            return HttpResponseRedirect("/personas/location/{}".format(location.slug))

        else:
            print (location_form.errors)

    else:
        location_form = LocationForm(story=story)

    return render(request, 'personas/add_location.html', {
        'slug': story_title_slug, 'story':story, 'locations': locations,
        'location_form':location_form, 'mainmap':mainmap})


@login_required
def add_nation(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)

    nations = Nation.objects.filter(location__story=story)

    if request.method == 'POST':

        nation_form = NationForm(request.POST, request.FILES or None, story=story)

        if nation_form.is_valid():
            nation = nation_form.save(commit=False)
            nation.creator = request.user
            nation.story = story
            nation.slug = slugify(
                "{}-{}".format(story.title, nation.name))
            nation.save()

            return HttpResponseRedirect("/personas/nation/{}".format(nation.slug))

        else:
            print (nation_form.errors)

    else:
        nation_form = NationForm(story=story)

    return render(request, 'personas/add_nation.html', {
        'slug': story_title_slug, 'story':story, 'nations': nations,
        'nation_form':nation_form})


@login_required
def add_gallery_image(request, storyobject_slug):


    storyobject = get_object_or_404(StoryObject, slug=storyobject_slug)
    story = storyobject.story

    if request.method == 'POST':
        image_form = GalleryImageForm(request.POST, request.FILES)

        creator = request.user

        if image_form.is_valid():
            image = image_form.save(commit=False)
            image.creator = creator
            image.storyobject = storyobject

            image.save()

            return HttpResponseRedirect("")

        else:
            print (image_form.errors)

    else:

        image_form = GalleryImageForm()

    return render(request, 'personas/add_gallery_image.html',
        {'image_form': image_form, 'storyobject':storyobject, 'story':story})


@login_required
def add_mainmap(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)

    if request.method == 'POST':

        mainmap_form = MainMapForm(request.POST)

        if mainmap_form.is_valid():
            mainmap = mainmap_form.save(commit=False)
            mainmap.creator = request.user
            mainmap.story = story
            mainmap.slug = slugify("{}-{}".format(story.title, mainmap.name))
            mainmap.save()

            return HttpResponseRedirect("/personas/mainmap/{}".format(mainmap.slug))

        else:
            print (mainmap_form.errors)

    else:
        mainmap_form = MainMapForm(story=story)

    return render(request, 'personas/add_mainmap.html', {
        'slug': story_title_slug, 'story':story,
        'mainmap_form':mainmap_form})


# Edit and Delete Views

@login_required
def delete_skill(request, pk, template_name='personas/delete_skill.html'):
    skill = Skill.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(skill=skill)
    if request.user == storyobject.creator:
        if request.method=='POST':
            skill.delete()
            return TemplateResponse(request, 'personas/redirect_template.html',
         {'redirect_url':'/personas/storyobject/{}/#skills'.format(storyobject.slug)})
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': skill})

@login_required
def edit_skill(request, pk, template_name='personas/edit_skill.html'):
    skill = Skill.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(skill=skill)
    story = storyobject.story
    form = SkillForm(request.POST or None, instance=skill, storyobject=storyobject)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, 'personas/redirect_template.html',
         {'redirect_url':'/personas/storyobject/{}/#skills'.format(storyobject.slug)})
    return render(request, template_name, {'form': form, 'storyobject': storyobject,
        'skill': skill, 'story':story})


@login_required
def delete_combat_info(request, pk, template_name='personas/delete_combat_info.html'):
    combat_info = CombatInfo.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(combatinfo=combat_info)
    if request.user == storyobject.creator:
        if request.method=='POST':
            combat_info.delete()
            return TemplateResponse(request, 'personas/redirect_template.html',
             {'redirect_url':'/personas/storyobject/{}/#skills'.format(
                storyobject.slug)})
    else:
        return HttpResponse("You do not have permission to edit this.")
    return render(request, template_name, {'object': combat_info})

@login_required
def edit_combat_info(request, pk, template_name='personas/edit_combat_info.html'):
    combat_info = CombatInfo.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(combatinfo=combat_info)
    story = storyobject.story
    form = CombatInfoForm(request.POST or None, instance=combat_info)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, 'personas/redirect_template.html',
         {'redirect_url':'/personas/storyobject/{}/#combat'.format(storyobject.slug)})
    return render(request, template_name, {'form': form, 'storyobject': storyobject,
        'combat_info': combat_info, 'story':story})


@login_required
def delete_relationship(request, pk, template_name='personas/delete_relationship.html'):
    relationship = Relationship.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(id=relationship.from_storyobject_id)
    if request.user == storyobject.creator:
        if request.method=='POST':
            relationship.delete()
            return TemplateResponse(request, 'personas/redirect_template.html',
             {'redirect_url':'/personas/storyobject/{}/#details'.format(
                storyobject.slug)})
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': relationship})


@login_required
def edit_relationship(request, pk, template_name='personas/edit_relationship.html'):
    relationship = Relationship.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(id=relationship.from_storyobject_id)
    story = storyobject.story
    form = RelationshipForm(request.POST or None, instance=relationship, story=story)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, 'personas/redirect_template.html',
         {'redirect_url':'/personas/storyobject/{}/#details'.format(
            storyobject.slug)})
    return render(request, template_name, {'form': form, 'from_storyobject':storyobject,
        'relationship': relationship, 'story':story})


@login_required
def delete_statistic(request, pk, template_name='personas/delete_statistic.html'):
    statistic = Statistic.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(statistic=statistic)
    if request.user == storyobject.creator:
        if request.method=='POST':
            statistic.delete()
            return TemplateResponse(request, 'personas/redirect_template.html',
             {'redirect_url':'/personas/storyobject/{}/#abilities'.format(
                storyobject.slug)})
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': statistic})


@login_required
def edit_statistic(request, pk, template_name='personas/edit_statistic.html'):
    statistic = Statistic.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(statistic=statistic)
    story = storyobject.story
    form = StatisticForm(request.POST or None, instance=statistic, storyobject=storyobject)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, 'personas/redirect_template.html',
         {'redirect_url':'/personas/storyobject/{}/#abilities'.format(storyobject.slug)})
    return render(request, template_name, {'form': form, 'storyobject':storyobject,
        'statistic': statistic, 'story':story})


@login_required
def delete_ability(request, pk, template_name='personas/delete_ability.html'):
    ability = Ability.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(ability=ability)
    if request.user == storyobject.creator:
        if request.method=='POST':
            ability.delete()
            return TemplateResponse(request, 'personas/redirect_template.html',
             {'redirect_url':'/personas/storyobject/{}/#details'.format(
                storyobject.slug)})
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': ability})


@login_required
def edit_ability(request, pk, template_name='personas/edit_ability.html'):
    ability = Ability.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(ability=ability)
    story = storyobject.story
    form = AbilityForm(request.POST or None, instance=ability)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, 'personas/redirect_template.html',
         {'redirect_url':'/personas/storyobject/{}/#abilities'.format(storyobject.slug)})
    return render(request, template_name, {'form': form, 'storyobject': storyobject,
        'ability': ability, 'story':story})


@login_required
def delete_aspect(request, pk, template_name='personas/delete_aspect.html'):
    aspect = Aspect.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(aspect=aspect)
    if request.user == storyobject.creator:
        if request.method=='POST':
            aspect.delete()
            return TemplateResponse(request, 'personas/redirect_template.html',
             {'redirect_url':'/personas/storyobject/{}/#details'.format(
                storyobject.slug)})
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': aspect})


@login_required
def edit_aspect(request, pk, template_name='personas/edit_aspect.html'):
    aspect = Aspect.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(aspect=aspect)
    story = storyobject.story
    form = AspectForm(request.POST or None, instance=aspect)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, 'personas/redirect_template.html',
         {'redirect_url':'/personas/storyobject/{}/#details'.format(storyobject.slug)})
    return render(request, template_name, {'form': form, 'storyobject':storyobject, 'aspect': aspect,
        'story':story})


@login_required
def delete_storyobject(request, pk, template_name='personas/delete_storyobject.html'):
    storyobject = StoryObject.objects.get(pk=pk)
    if request.user == storyobject.creator:
        if request.method=='POST':
            storyobject.delete()
            return HttpResponseRedirect('/personas/')
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': storyobject})


@login_required
def edit_storyobject(request, pk, template_name='personas/edit_storyobject.html'):
    storyobject = StoryObject.objects.get(pk=pk)
    story = storyobject.story
    user = request.user
    form = StoryObjectForm(request.POST or None, request.FILES or None, instance=storyobject,
        story=story)
    if form.is_valid():
        form.save(creator=storyobject.creator, story=story)
        return HttpResponseRedirect('/personas/storyobject/{}'.format(storyobject.slug))
    return render(request, template_name, {'form': form, 'storyobject':storyobject,
        'story':story})


@login_required
def delete_place(request, pk, template_name='personas/delete_place.html'):
    place = Place.objects.get(pk=pk)
    if request.user == place.creator:
        if request.method=='POST':
            place.delete()
            return HttpResponseRedirect('/personas/')
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': place})


@login_required
def edit_place(request, pk, template_name='personas/edit_place.html'):
    place = Place.objects.get(pk=pk)
    story = place.story
    user = request.user
    form = PlaceForm(request.POST or None, request.FILES or None, instance=place,
        story=story)
    if form.is_valid():
        form.save(creator=place.creator, story=story)
        return HttpResponseRedirect('/personas/place/{}'.format(place.slug))
    return render(request, template_name, {'form': form, 'place':place,
        'story':story})



@login_required
def delete_story(request, pk, template_name='personas/delete_story.html'):
    story = Story.objects.get(pk=pk)
    if request.user == story.author:
        if request.method=='POST':
            story.delete()
            return HttpResponseRedirect('/personas/')
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': story})


@login_required
def edit_story(request, pk, template_name='personas/edit_story.html'):
    story = Story.objects.get(pk=pk)
    user = request.user
    form = StoryForm(request.POST or None, request.FILES or None, instance=story)
    if form.is_valid():
        form.save(author=story.author)
        return HttpResponseRedirect('/personas/story/{}'.format(story.slug))
    return render(request, template_name, {'form': form, 'story':story})


@login_required
def delete_location(request, pk, template_name='personas/delete_location.html'):
    location = Location.objects.get(pk=pk)
    story = Story.objects.get(location=location)
    if request.user == location.creator:
        if request.method=='POST':
            location.delete()
            return HttpResponseRedirect('/personas/{}'.format(story.slug))
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': location})


@login_required
def edit_location(request, pk, template_name='personas/edit_location.html'):
    location = Location.objects.get(pk=pk)
    story = location.story
    user = request.user
    form = LocationForm(request.POST or None, request.FILES or None, instance=location, story=story)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/personas/location/{}'.format(location.slug))
    return render(request, template_name, {'form': form, 'location':location, 'story':story})


@login_required
def delete_chapter(request, pk, template_name='personas/delete_chapter.html'):
    chapter = Chapter.objects.get(pk=pk)
    story = Story.objects.get(chapter=chapter)
    if request.user == story.author:
        if request.method=='POST':
            chapter.delete()
            return HttpResponseRedirect('/personas/story/{}'.format(story.slug))
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': chapter})


@login_required
def edit_chapter(request, pk, template_name='personas/edit_chapter.html'):
    chapter = Chapter.objects.get(pk=pk)
    story = chapter.story
    user = request.user
    form = ChapterForm(request.POST or None, request.FILES or None, instance=chapter)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/personas/chapter/{}'.format(chapter.slug))
    return render(request, template_name, {'form': form, 'object':chapter, 'story':story})


@login_required
def delete_scene(request, pk, template_name='personas/delete_scene.html'):
    scene = Scene.objects.get(pk=pk)
    story = Story.objects.get(chapter__scene=scene)
    if request.user == story.author:
        if request.method=='POST':
            scene.delete()
            return HttpResponseRedirect('/personas/story/{}'.format(story.slug))
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': scene})


@login_required
def edit_scene(request, pk, template_name='personas/edit_scene.html'):
    scene = Scene.objects.get(pk=pk)
    user = request.user
    story = Story.objects.get(chapter__scene=scene)
    form = SceneForm(request.POST or None, request.FILES or None, instance=scene, story=story)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/personas/scene/{}'.format(scene.slug))
    return render(request, template_name, {'form': form, 'object':scene, 'story':story})


@login_required
def delete_note(request, pk, template_name='personas/delete_note.html'):
    note = Note.objects.get(pk=pk)

    if note.storyobject:
        target = note.storyobject
    elif note.location:
        target = note.location
    elif note.story:
        target = note.story
    elif note.chapter:
        target = note.chapter
    else:
        target = note.scene

    pointer = return_object(target)

    if request.user == note.creator:
        if request.method=='POST':
            note.delete()
            return HttpResponseRedirect('/personas/{}/{}'.format(pointer,
                target.slug))
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': note})


@login_required
def edit_note(request, pk, template_name='personas/edit_note.html'):
    note = Note.objects.get(pk=pk)

    if note.storyobject:
        target = note.storyobject
    elif note.location:
        target = note.location
    elif note.story:
        target = note.story
    elif note.chapter:
        target = note.chapter
    else:
        target = note.scene

    pointer = return_object(target)

    form = NoteForm(request.POST or None, instance=note)
    if form.is_valid():
        form.save(creator=note.creator)
        return HttpResponseRedirect('/personas/{}/{}'.format(pointer,
            target.slug))
    return render(request, template_name, {'form': form, 'object': note})


@login_required
def delete_nation(request, pk, template_name='personas/delete_nation.html'):
    nation = Nation.objects.get(pk=pk)
    story = Story.objects.get(nation=nation)
    if request.user == story.author:
        if request.method=='POST':
            nation.delete()
            return HttpResponseRedirect('/personas/{}'.format(story.slug))
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': nation})


@login_required
def edit_nation(request, pk, template_name='personas/edit_nation.html'):
    nation = Nation.objects.get(pk=pk)
    story = Story.objects.get(nation=nation)
    user = request.user
    form = NationForm(request.POST or None, request.FILES or None, instance=nation, story=story)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/personas/nation/{}'.format(nation.slug))
    return render(request, template_name, {'form': form, 'nation':nation, 'story':story})


@login_required
def delete_gamestats(request, pk, template_name='personas/delete_gamestats.html'):
    gamestats = GameStats.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(gamestats=gamestats)
    if request.user == storyobject.creator:
        if request.method=='POST':
            gamestats.delete()
            return HttpResponseRedirect('/personas/storyobject/{}'.format(storyobject.slug))
    else:
        return HttpResponse("You do not have permission to delete this.")
    return render(request, template_name, {'object': gamestats})


@login_required
def edit_gamestats(request, pk, template_name='personas/edit_gamestats.html'):
    gamestats = GameStats.objects.get(pk=pk)
    storyobject = StoryObject.objects.get(gamestats=gamestats)
    story = storyobject.story
    form = GameStatsForm(request.POST or None, instance=gamestats)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/personas/storyobject/{}'.format(storyobject.slug))
    return render(request, template_name, {'form': form, 'object':gamestats, 'story':story,
        'storyobject': storyobject})
