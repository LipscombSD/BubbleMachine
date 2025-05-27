from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """Custom renderer to standardize API responses"""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {
            'version': 'v1',
            'err': None,
            'data': data
        }

        # Handle error responses
        if renderer_context and renderer_context.get('response'):
            response = renderer_context['response']
            if response.status_code >= 400:
                response_data['err'] = data
                response_data['data'] = None

        return super().render(response_data, accepted_media_type, renderer_context)