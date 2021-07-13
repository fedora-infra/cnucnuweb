# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests

from anitya.lib.backends import BaseBackend


class SourceforgeGitBackend(BaseBackend):
    """The custom class for projects hosted on sourceforge.net.

    This backend allows to specify a version_url and a regex that will
    be used to retrieve the version information.
    """

    name = "Sourceforge (git)"
    examples = [
        "https://sourceforge.net/p/ubuntuzilla/ubuntuzilla/ref/master/tags/",
        "https://sourceforge.net/p/eclipse-cs/git/ref/master/tags/",
    ]

    @classmethod
    def get_version(cls, project):
        """Method called to retrieve the latest version of the projects
        provided, project that relies on the backend of this plugin.

        :arg Project project: a :class:`anitya.db.models.Project` object whose backend
            corresponds to the current plugin.
        :return: the latest version found upstream
        :return type: str
        :raise AnityaPluginException: a
            :class:`anitya.lib.exceptions.AnityaPluginException` exception
            when the version cannot be retrieved correctly

        """
        return cls.get_ordered_versions(project)[-1]

    @classmethod
    def get_version_url(cls, project):
        """Method called to retrieve the url used to check for new version
        of the project provided, project that relies on the backend of this plugin.

        Attributes:
            project (:obj:`anitya.db.models.Project`): Project object whose backend
                corresponds to the current plugin.

        Returns:
            str: url used for version checking
        """
        url = ""
        if project.version_url:
            url = project.version_url

        else:
            namespace, repo = cls.get_namespace_repo(project)
            url = f"https://sourceforge.net/p/{namespace}/{repo}/ref/master/tags/"

        return url

    @classmethod
    def get_namespace_repo(cls, project):
        prefix = "https://sourceforge.net/p/"

        namespace = repo = url = ""
        if project.homepage.startswith(prefix):
            url = project.homepage[len(prefix) :]

        if url:
            namespace, repo = url.split("/")[0:2]
            url = f"https://sourceforge.net/p/{namespace}/{repo}/ref/master/tags/"

        return namespace, repo

    @classmethod
    def get_versions(cls, project):
        """Method called to retrieve all the versions (that can be found)
        of the projects provided, project that relies on the backend of
        this plugin.

        :arg Project project: a :class:`anitya.db.models.Project` object whose backend
            corresponds to the current plugin.
        :return: a list of all the possible releases found
        :return type: list
        :raise AnityaPluginException: a
            :class:`anitya.lib.exceptions.AnityaPluginException` exception
            when the versions cannot be retrieved correctly

        """
        namespace, repo = cls.get_namespace_repo_url(project)
        git_tag_request = requests.get(project.get_version_url())

        soup = BeautifulSoup(git_tag_request.content, "html.parser")

        def is_release_tag_link(tag):
            link_prefix = f"/p/{namespace}/{repo}/ci/"
            return (
                tag.has_attr("href")
                and tag.attrs["href"].startswith(link_prefix)
                and len(tag.contents) == 1
            )

        release_tags = []
        for release_tag in soup.find_all(is_release_tag_link):
            release_tag_text = release_tag.contents[0]
            release_tags.append(release_tag_text)

        return release_tags
