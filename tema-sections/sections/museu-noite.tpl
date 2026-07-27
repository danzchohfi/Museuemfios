{# MUSEU EM FIOS — a noite: o layout quebra pro escuro (gradiente pro céu
   noturno) e mostra o momento de uso do produto — o vídeo institucional.

   O player é grande de propósito (pedido do cliente): quase a largura toda do
   wrap no desktop, sangrando as bordas no mobile.

   O campo do vídeo guarda só o ID do YouTube, não a URL inteira — assim o
   embed continua sempre em modo nocookie, sem depender de quem cola o link. #}

<section class="mf-noite">
    <div class="mf-wrap">
        {% if section.settings.eyebrow %}
            <p class="mf-eyebrow" data-reveal>{{ section.settings.eyebrow }}</p>
        {% endif %}
        {% if section.settings.titulo %}
            <h2 class="mf-h2" data-reveal>{{ section.settings.titulo | raw }}</h2>
        {% endif %}
        {% if section.settings.apoio %}
            <div class="mf-noite__apoio" data-reveal>{{ section.settings.apoio | raw }}</div>
        {% endif %}
        {% if section.settings.video_id %}
            <div class="mf-noite__video" data-reveal>
                <iframe src="https://www.youtube-nocookie.com/embed/{{ section.settings.video_id }}?rel=0"
                        title="{{ section.settings.video_titulo }}"
                        loading="lazy"
                        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen></iframe>
            </div>
        {% endif %}
    </div>
</section>

{% schema %}
{
  "name": "t:names.museu_noite",
  "class": "mf-secao-noite",
  "limit": 1,
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "eyebrow",
      "label": "t:settings.museu_eyebrow",
      "default": "t:defaults.museu_ritual"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "titulo",
      "label": "t:settings.museu_titulo"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "apoio",
      "label": "t:settings.museu_apoio"
    },
    { "type": "header", "content": "t:names.museu_video" },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "video_id",
      "label": "t:settings.museu_video_id",
      "default": "Q2dJHg6M9jw"
    },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "video_titulo",
      "label": "t:settings.museu_video_titulo",
      "default": "t:defaults.museu_video_titulo"
    }
  ],
  "enabled_on": {
    "page_templates": ["home"]
  },
  "presets": [
    {
      "name": "t:names.museu_noite",
      "category": "t:categories.museu",
      "settings": {
        "eyebrow": "t:defaults.museu_ritual",
        "video_id": "Q2dJHg6M9jw"
      }
    }
  ]
}
{% endschema %}
