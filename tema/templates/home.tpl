{# Detect presence of features that remove empty placeholders #}

{% set has_main_slider = settings.slider and settings.slider is not empty %}
{% set has_mobile_slider = settings.toggle_slider_mobile and settings.slider_mobile and settings.slider_mobile is not empty %}
{% set has_informative_banners = settings.banner_services and (settings.banner_services_01_title or settings.banner_services_02_title or settings.banner_services_03_title or settings.banner_services_04_title) %}
{% set has_category_banners =  settings.banner_01_show or settings.banner_02_show or settings.banner_03_show %}
{% set has_welcome_message = settings.welcome_message %}
{% set has_image_text_modules = settings.module_01_show or settings.module_02_show or settings.module_03_show %}
{% set has_video = settings.video_embed %}
{% set has_instafeed = store.instagram and settings.show_instafeed and store.hasInstagramToken() %}

{% set show_help = not (has_main_slider or has_mobile_slider or has_category_banners or has_image_text_modules or has_video or has_instafeed or has_informative_banners) and not has_products %}

{% set show_component_help = params.preview %}

{% if not params.preview %}
	{% set admin_link = is_theme_draft ? '/admin/themes/settings/draft/' : '/admin/themes/settings/active/' %}
{% endif %}

{#  **** Features Order ****  #}
{% set newArray = [] %}

{# Museu em Fios — home no conceito V5 "O Fio" (aprovado):
   entardecer + meada 3D + manifesto; as seções nativas correm sobre o fundo
   escuro (.v4-fundo) enquanto o fio-costura (museu-3d.js) atravessa a página.
   Para VOLTAR ao conceito V1 (editorial claro): troque hero-fio/manifesto-fio
   por hero.tpl + marquee.tpl + manifesto.tpl, remova o wrapper .v4-fundo e o
   certificado.tpl, re-inclua passos.tpl + kit.tpl após o container e apague
   as classes/links condicionais de home no layouts/layout.tpl (ver README). #}

{% include 'snipplets/museu/hero-fio.tpl' %}
{% include 'snipplets/museu/manifesto-fio.tpl' %}

<div class="v4-fundo">
	<div class="js-home-sections-container">
		{% for i in 0..8 %}
			{% set section = 'home_order_position_' ~ i %}
			{% set section_select = attribute(settings, section) %}

			{% if section_select not in newArray %}
				{% include 'snipplets/home/home-section-switch.tpl' %}
				{% set newArray = newArray|merge([section_select]) %}
			{% endif %}

		{% endfor %}

		{#  **** Hidden Sections ****  #}
		{% if show_component_help %}
			<div style="display:none">
				{% for section_select in ['slider', 'products', 'informatives', 'categories', 'welcome', 'video', 'instafeed', 'modules'] %}
					{% if section_select not in newArray %}
						{% include 'snipplets/home/home-section-switch.tpl' %}
					{% endif %}
				{% endfor %}
			</div>
		{% endif %}
	</div>

	{# Fecho da narrativa: a faixa do certificado #}

	{% include 'snipplets/museu/certificado.tpl' %}
</div>

{% if settings.home_promotional_popup %}
    {% include 'snipplets/home/home-popup.tpl' %}
{% endif %}
