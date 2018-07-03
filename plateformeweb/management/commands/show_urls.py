from django.core.management import BaseCommand
from django.conf.urls import RegexURLPattern, RegexURLResolver
from django.core import urlresolvers


class Command(BaseCommand):

    def add_arguments(self, parser):

        pass

    def handle(self, *args, **kwargs):

        urls = urlresolvers.get_resolver()
        all_urls = list()

        def func_for_sorting(i):
            if i.name is None:
                i.name = ''
            return i.lookup_str

        def show_urls(urls):
            for url in urls.url_patterns:
                if isinstance(url, RegexURLResolver):
                    show_urls(url)
                elif isinstance(url, RegexURLPattern):
                    all_urls.append(url)
        show_urls(urls)

        all_urls.sort(key=func_for_sorting, reverse=False)

        for url in all_urls:
            print('| {0.regex.pattern:50} | {0.name:50} | {0.lookup_str:20} | {0.default_args} |'.format(url))
