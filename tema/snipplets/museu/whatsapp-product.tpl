{# MUSEU EM FIOS — CTA de dúvidas no produto (WhatsApp da loja, se configurado) #}

{% if store.whatsapp %}
    <a class="mf-wa js-museu-wa" target="_blank" rel="noopener"
       href="{{ store.whatsapp }}"
       data-message="Olá! Estou vendo o {{ product.name }} e queria tirar uma dúvida antes de comprar.">
        {% include "snipplets/svg/whatsapp.tpl" with {svg_custom_class: "icon-inline"} %}
        Dúvidas sobre o kit? Fale com a gente
    </a>
{% endif %}
