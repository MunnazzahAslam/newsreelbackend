from django.contrib import admin
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


from .models import Poll, Choice, Meme, Article, PSA, Repost, Post, Comment


class ChoiceInline(admin.StackedInline):
    model = Choice
    readonly_fields = ('votes', 'voters')
    extra = 0
    max_num = 5
    can_delete = False


class PollAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    search_fields = ('question', )
    readonly_fields = ('votes', )


class PollInline(admin.StackedInline):
    model = Poll
    extra = 0
    max_num = 1
    can_delete = False


class PSAInline(admin.StackedInline):
    model = PSA
    extra = 0
    max_num = 1
    can_delete = False


class MemeInline(admin.StackedInline):
    model = Meme
    extra = 0
    max_num = 1
    can_delete = False


class RepostInline(admin.StackedInline):
    model = Repost
    extra = 0
    max_num = 1
    can_delete = False


class ArticleInline(admin.StackedInline):
    model = Article
    extra = 0
    max_num = 1
    can_delete = False


INLINE_CLASSES = {
    'psa': PSAInline,
    'poll': PollInline,
    'meme': MemeInline,
    'repost': RepostInline,
    'article': ArticleInline,
}


class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('type', 'category', 'slug', 'comments', 'upvotes', 'author', 'created_at')}),
    )
    list_filter = ('type', )
    list_display = ('id', 'type', 'author')
    actions = ('generate_slug', )
    readonly_fields = ('comments', 'upvotes', 'created_at')
    inlines = (PSAInline, MemeInline, RepostInline, ArticleInline)

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if not obj:
            return []

        inline_class = INLINE_CLASSES[obj.type]
        if inline_class:
            inline = inline_class(self.model, self.admin_site)
            inlines.append(inline)

        return inlines

    def generate_slug(self, request, queryset):
        for post in queryset:
            post_id = post.id
            post_type = post.type

            if post_type == 'article':
                slug = '%s %d' % (post.article.title, post_id)
            elif post_type == 'psa':
                slug = '%s %d' % (post.psa.text, post_id)
            elif post_type in ('meme', 'repost'):
                username = post.author.username
                slug = '%s %s %d' % (username, post_type, post_id)
            else:
                question = post.poll.question
                slug = '%s %d' % (question, post_id)

            post.slug = slugify(slug)
            post.save()

        message = 'Successfully updated %d posts' % queryset.count()
        messages.success(request, message)

    generate_slug.short_description = _("Generate slug")


class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', )
    list_display = ('id', 'post', 'author', 'parent_comment')


admin.site.register(PSA)
admin.site.register(Meme)
admin.site.register(Repost)
admin.site.register(Article)
admin.site.register(Poll, PollAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
