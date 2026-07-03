from django.utils.deprecation import MiddlewareMixin


class NoCacheMiddleware(MiddlewareMixin):
    """Middleware to prevent caching of API responses."""
    
    def process_response(self, request, response):
        # Apply no-cache headers to API endpoints
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Cache-Control'] = 'no-store'
        
        # Template responses - minimal caching
        elif request.path == '/' or request.path.endswith('.html'):
            response['Cache-Control'] = 'no-cache, must-revalidate, max-age=3600'
        
        return response
