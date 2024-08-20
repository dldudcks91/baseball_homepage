import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class QueryCountDebugMiddleware(MiddlewareMixin):
    def process_request(self, request):
        self.start_time = time.time()
        self.queries_before = len(connection.queries)

    def process_response(self, request, response):
        total_time = time.time() - self.start_time
        queries_after = len(connection.queries)
        
        query_count = queries_after - self.queries_before
        logger.debug(f"Path: {request.path}, Query Count: {query_count}, Total Time: {total_time:.3f}s")
        return response