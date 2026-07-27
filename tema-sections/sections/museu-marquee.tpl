{# MUSEU EM FIOS — faixa marquee com a endline e os avisos que rodam.

   Cada frase é um block. O trilho é duplicado no template pra emenda do loop
   ficar invisível — por isso o laço roda duas vezes sobre os mesmos blocks. #}

{% if section.blocks | length > 0 %}
<div class="mf-marquee" aria-hidden="true">
    <div class="mf-marquee__trilho">
        {% for i in 1..2 %}
            {% for block in section.blocks %}
                {% include 'blocks/museu-frase.tpl' with { block: block } %}
            {% endfor %}
        {% endfor %}
    </div>
</div>
{% endif %}

{% schema %}
{
  "name": "t:names.museu_marquee",
  "wrapper": "div",
  "class": "mf-secao-marquee",
  "max_blocks": 8,
  "blocks": [
    { "type": "museu-frase" }
  ],
  "settings": [],
  "presets": [
    {
      "name": "t:names.museu_marquee",
      "category": "t:categories.museu"
    }
  ]
}
{% endschema %}
