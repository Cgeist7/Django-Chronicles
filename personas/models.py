from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from PIL import Image
from django_markdown.models import MarkdownField
#from django.contrib.gis.db import models as gismodels
#from jsonfield import JSONField
#from djgeojson.fields import PointField
#from treasuremap.fields import LatLongField
import collections


class Nation(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, default=1)
    might = models.PositiveSmallIntegerField(default=0)
    intrigue = models.PositiveSmallIntegerField(default=0)
    magic = models.PositiveSmallIntegerField(default=0)
    wealth = models.PositiveSmallIntegerField(default=0)
    influence = models.PositiveSmallIntegerField(default=0)
    defense = models.PositiveSmallIntegerField(default=0)
    image = models.ImageField(upload_to='nation_images/%Y/%m/%d', default='nation_images/nothing.jpg')

    story = models.ForeignKey('Story')

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify("{}-{}".format(self.story.title, self.name))
        super(Nation, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=128)
    creator = models.ForeignKey(User, blank=True, null=True)
    image = models.ImageField(upload_to='location_images/%Y/%m/%d', default='location_images/nowhere.jpg')
    terrain = models.CharField(max_length=128)
    features = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    nation = models.ForeignKey(Nation, blank=True)
    latitude = models.FloatField(default=50.0)
    longitude = models.FloatField(default=-1.0)
    story = models.ForeignKey('Story', default=1)
    #geom = PointField()

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify("{}-{}".format(self.story.title, self.name))
        super(Location, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


class Aspect(models.Model):
    CORE = "CO"
    VALUES = "VA"
    BACKGROUND = "BA"
    FLAW = "FL"

    ASPECT_TYPE_CHOICES = (
        (CORE, "Core"),
        (VALUES, "Values"),
        (BACKGROUND, "Background"),
        (FLAW, "Flaw")
        )

    label = models.CharField(max_length=12, choices=ASPECT_TYPE_CHOICES, default="CO", blank=True)
    name = models.CharField(max_length=128)
    storyobject = models.ForeignKey('StoryObject')

    def save(self, *args, **kwargs):
        super(Aspect, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


class Ability(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    storyobject = models.ForeignKey('StoryObject', null=True, blank=True)
    item = models.ForeignKey('Item', null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Ability, self).save(*args, **kwargs)


    def __str__(self):
        return "{}: {}".format(self.name, self.description)


class Note(models.Model):
    creator = models.ForeignKey(User, default=0)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    storyobject = models.ForeignKey("StoryObject", blank=True, null=True)
    location = models.ForeignKey("Location", blank=True, null=True)
    item = models.ForeignKey("Item", blank=True, null=True)
    organization = models.ForeignKey("Organization", blank=True, null=True)
    nation = models.ForeignKey("Nation", blank=True, null=True)
    scene = models.ForeignKey("Scene", blank=True, null=True)
    chapter = models.ForeignKey("Chapter", blank=True, null=True)
    story = models.ForeignKey("Story", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        super(Note, self).save(*args, **kwargs)

    def __str__(self):
        return self.content


class GalleryImage(models.Model):
    creator = models.ForeignKey(User)
    image = models.ImageField(upload_to='content_images/%Y/%m/%d', default='content_images/nothing.jpg')
    title = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now=True)
    storyobject = models.ForeignKey("StoryObject", blank=True, null=True)
    location = models.ForeignKey("Location", blank=True, null=True)
    item = models.ForeignKey("Item", blank=True, null=True)
    organization = models.ForeignKey("Organization", blank=True, null=True)
    nation = models.ForeignKey("Nation", blank=True, null=True)
    scene = models.ForeignKey("Scene", blank=True, null=True)
    chapter = models.ForeignKey("Chapter", blank=True, null=True)
    story = models.ForeignKey("Story", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        super(GalleryImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class ScratchPad(models.Model):
    creator = models.ForeignKey(User, default=0)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    storyobject = models.ForeignKey("StoryObject", blank=True, null=True)

    def __str__(self):
        return self.content


class Communique(models.Model):
    author = models.ForeignKey("StoryObject", related_name="Author")
    receiver = models.ForeignKey("StoryObject", related_name="Receiver")
    date = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=140)
    rating = models.PositiveSmallIntegerField(default=0)

    def save(self, author, *args, **kwargs):
        self.author = author
        super(Communique, self).save(*args, **kwargs)

    def __str__(self):
        return "{} -- {} to {}".format(self.content, self.author, self.receiver,)


class Skill(models.Model):
    TYPE_1 = "Type_1"
    TYPE_2 = "Type_2"
    TYPE_3 = "Type_3"
    TYPE_4 = "Type_4"

    SKILL_TYPES = (
        (TYPE_1, "Type_1"),
        (TYPE_2, "Type_2"),
        (TYPE_3, "Type_3"),
        (TYPE_4, "Type_4"))

    name = models.CharField(max_length=32)
    value = models.CharField(max_length=32, default=0)
    s_type = models.CharField(max_length=32, choices=SKILL_TYPES, verbose_name="Skill Type", default="Type_1")
    storyobject = models.ForeignKey('StoryObject')
    description = models.TextField(blank=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.value)


class Statistic(models.Model):
    TYPE_1 = "Type_1"
    TYPE_2 = "Type_2"
    TYPE_3 = "Type_3"
    TYPE_4 = "Type_4"

    STAT_TYPES = (
        (TYPE_1, "Type_1"),
        (TYPE_2, "Type_2"),
        (TYPE_3, "Type_3"),
        (TYPE_4, "Type_4"))

    name = models.CharField(max_length=32)
    value = models.CharField(max_length=32, default=0)
    stat_type = models.CharField(
        max_length=32, choices=STAT_TYPES, verbose_name="Statistic Type",
         default="Type_1")
    storyobject = models.ForeignKey('StoryObject')
    description = models.TextField(blank=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.value)


class CombatInfo(models.Model):
    title = models.CharField(max_length=32)
    data = models.CharField(max_length=128, default=0)
    storyobject = models.ForeignKey('StoryObject')

    def __str__(self):
        return "{}: {}".format(self.title, self.data)


class Item(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    storyobject = models.ForeignKey('StoryObject', blank=True, null=True)
    story = models.ForeignKey('Story', blank=True, null=True)

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify("{}-{}".format(self.story.title, self.name))
        super(Item, self).save(*args, **kwargs)


    def __str__(self):
        return "{}: {}".format(self.name, self.description)


class StoryObject(models.Model):

    CHARACTER = "Character"
    CREATURE = "Creature"
    THING = "Thing"
    ABSTRACT = "Abstract"

    CHAR_CHOICES = (
        (CHARACTER, "Character"),
        (CREATURE, "Creature"),
        (THING, "Thing"),
        (ABSTRACT, "Abstract"))

    creator = models.ForeignKey(User, unique=False, blank=True)
    name = models.CharField(max_length=128, unique=False)
    story = models.ForeignKey('Story', default=1)
    c_type = models.CharField(choices=CHAR_CHOICES, 
        max_length=32, default="Character", verbose_name="Story Object Type",
        help_text="Select a story object category.")
    role = models.CharField(max_length=256)
    description = MarkdownField(blank=True)
    nationality = models.ForeignKey(Nation, blank=True, null=True)
    base_of_operations = models.ForeignKey(Location, related_name='active_in', 
        blank=True, null=True )

    image = models.ImageField(
        upload_to='profile_images/%Y/%m/%d/%H/%M/%S', default='profile_images/shadow_figure.jpeg')
    slug = models.SlugField(unique=True)

    stats_toggle = models.BooleanField(default=True,
     help_text="Check to enable statistics for this story object.",
        verbose_name="Enable Statistics?")
    skill_toggle = models.BooleanField(default=True,
     help_text="Check to enable skills for this story object.",
        verbose_name="Enable Skills?")
    combat_toggle = models.BooleanField(default=True,
     help_text="Check to enable combat info for this story object.",
        verbose_name="Enable Combat Info?")
    gallery_toggle = models.BooleanField(default=True,
     help_text="Check to enable gallery images for this story object.",
        verbose_name="Enable Gallery Images?")
    social_toggle = models.BooleanField(default=True,
     help_text="Check to enable social functionality for this story object.",
        verbose_name="Enable Social Functions?")

    def save(self, slug=None, creator=None, *args, **kwargs):
        slug = slugify("{}-{}".format(self.story.title, self.name))
        super(StoryObject, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Relationship(models.Model):

    from_storyobject = models.ForeignKey(StoryObject, related_name="from_storyobject",
        verbose_name="Subject of Relationship")
    to_storyobject = models.ForeignKey(StoryObject, related_name="to_storyobject",
        verbose_name="Object of Relationship")

    relationship_class = models.CharField(max_length=32,
        default='Ally',
        verbose_name="Defining Emotion")

    weight = models.CharField(default="50", max_length=64,
        verbose_name="Strength of the relationship")

    relationship_description = models.CharField(max_length=128, unique=False)

    def __str__(self):
        return '{} >> {} >> {} ({}: {})'.format(
            self.from_storyobject, self.relationship_class,
            self.to_storyobject, self.relationship_description, self.weight)


class Organization(models.Model):
    name = models.CharField(max_length=128)
    creator = models.ForeignKey(User, blank=True, null=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(StoryObject, through='Membership', blank=True)
    purpose = models.CharField(max_length=128)
    region = models.CharField(max_length=128)
    location = models.ForeignKey(Location)
    story = models.ForeignKey('Story')
    image = models.ImageField(upload_to='organization_images/%Y/%m/%d', default='organization_images/nothing.jpg')

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify("{}-{}".format(self.story.title, self.name))
        super(Organization, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Membership(models.Model):
    storyobject = models.ForeignKey(StoryObject)
    organization = models.ForeignKey(Organization)
    date_joined = models.DateField(auto_now=True)
    role = models.CharField(max_length=128)
    rank = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return "{} - Rank {} - {}".format(self.organization, self.rank, self.role)


class Scene(models.Model):

    PROCEDURAL = "Prodecural"
    ACTION = "Action"
    SUSPENSE = "Suspense"
    QUESTION = "Question"
    REVEAL = "Reveal"
    DRAMATIC = "Dramatic"

    SCENE_TYPE_CHOICES = (
        (DRAMATIC, "Dramatic"),
        (ACTION, "Action"),
        (SUSPENSE, "Suspense"),
        (QUESTION, "Question"),
        (REVEAL, "Reveal"),
        (PROCEDURAL, "Procedural"))

    UP = "Up"
    DOWN = "Down"
    NEUTRAL = "Neutral"

    RESOLUTION_CHOICES = (
        (UP, "Up"),
        (DOWN, "Down"),
        (NEUTRAL, "Neutral"))

    title = models.CharField(max_length=128)
    scene_type = models.CharField(max_length=32, choices=SCENE_TYPE_CHOICES, default="Dramatic")
    purpose = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    resolution = models.CharField(
        max_length=8, choices=RESOLUTION_CHOICES, default="Neutral")
    creator = models.ForeignKey(User, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True)
    publication_date = models.DateTimeField(auto_now=True)
    order = models.PositiveSmallIntegerField(default=1)
    storyobjects = models.ManyToManyField(StoryObject, blank=True)
    chapter = models.ForeignKey("Chapter")

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        slug = slugify("{}-{}".format(self.chapter.story.title, self.title))
        super(Scene, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Chapter(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, blank=True, null=True)
    story = models.ForeignKey("Story")
    number = models.PositiveSmallIntegerField(default=1,
        verbose_name="Chapter Number")

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify("{}-{}".format(self.story.title, self.title))
        super(Chapter, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Story(models.Model):
    SUPERS = 'Supers'
    FANTASY = 'Fantasy'
    HORROR = 'Horror'
    HISTORICAL = 'Historical'
    SCI_FI = 'Science-Fiction'
    WESTERN = 'Western'
    DRAMA = 'Drama'
    COMEDY = 'Comedy'
    CRIME = 'Crime'
    FABLE = 'Fable'
    MYSTERY = 'Mystery'

    GENRE_CHOICES = (
        (SUPERS, 'Supers'),
        (FANTASY, 'Fantasy'),
        (HORROR, 'Horror'),
        (HISTORICAL, 'Historical'),
        (SCI_FI, "Science Fiction"),
        (WESTERN, 'Western'),
        (DRAMA, 'Drama'),
        (COMEDY, 'Comedy'),
        (CRIME, 'Crime'),
        (FABLE, 'Fable'),
        (MYSTERY, 'Mystery'),
    )

    LIGHT = "Light"
    DARK = "Dark"

    THEME_CHOICES = (
        (LIGHT, 'Light'),
        (DARK, 'Dark'))

    title = models.CharField(max_length=128)
    author = models.ForeignKey(User)
    publication_date = models.DateField(auto_now=True)
    setting = models.CharField(max_length=256)
    themes = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    genre = models.CharField(
        max_length=128, choices=GENRE_CHOICES, default='Fantasy')
    image = models.ImageField(
        upload_to='story_images/%Y/%m/%d', default='story_images/nobody.jpg')
    background = models.ImageField(
        upload_to='story_backgrounds/%Y/%m/%d', default='story_backgrounds/nothing.jpg')
    colour_theme = models.CharField(
        max_length=12, choices=THEME_CHOICES, default='Dark')
    map_tile = models.CharField(
        max_length=128, default="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
    skill_type_name_1 = models.CharField(
        max_length=24, default="General", blank=True)
    skill_type_name_2 = models.CharField(
        max_length=24, default="Investigative", blank=True)
    skill_type_name_3 = models.CharField(
        max_length=24, default="Combat", blank=True)
    skill_type_name_4 = models.CharField(
        max_length=24, default="Knowledge", blank=True)

    statistic_type_name_1 = models.CharField(
        max_length=24, default="Physical", blank=True)
    statistic_type_name_2 = models.CharField(
        max_length=24, default="Mental", blank=True)
    statistic_type_name_3 = models.CharField(
        max_length=24, default="Social", blank=True)
    statistic_type_name_4 = models.CharField(
        max_length=24, default="Magic", blank=True)


    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        super(Story, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class MainMap(models.Model):
    name = models.CharField(max_length=64)
    story = models.ForeignKey(Story)
    base_latitude = models.FloatField(blank=True)
    base_longitude = models.FloatField(blank=True)
    tiles = models.CharField(max_length=256, blank=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        super(MainMap, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    website = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='user_images/%Y/%m/%d', default='user_images/nobody.jpg')

    def __str__(self):
        return self.user.username



