---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

Publication records are generated from the LaTeX CV source in <a href="{{ "/cv/main.tex" | prepend: base_path }}">cv/main.tex</a>. A PDF version of the CV is available <a href="{{ "/files/cv.pdf" | prepend: base_path }}">here</a>.

{% include base_path %}

{% assign publications = site.publications | sort: "order" %}
{% assign current_section = "" %}
{% for post in publications %}
{% if post.section != current_section %}
{% assign current_section = post.section %}
<h2 class="archive__subtitle">{{ current_section }}</h2>
{% endif %}
{% include archive-single.html %}
{% endfor %}
