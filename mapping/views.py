from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .serializers import NIDFetchRequestSerializer, NIDMappingResponseSerializer, NIDWrapperSerializer
# from .services.mapper import map_nid_to_spdci  # commented out SPDCI mapping for now
from .services.client import NIDClient
from rest_framework import permissions

class NIDMappingView(APIView):
    """
    [Legacy] Push-based mapping endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        request=NIDWrapperSerializer,
        responses={200: NIDMappingResponseSerializer},
        description="Maps wrapped NID data to standardized SPDCI structure."
    )
    def post(self, request):
        serializer = NIDWrapperSerializer(data=request.data)
        if serializer.is_valid():
            nid_data = serializer.validated_data.get('nid')
            nin = nid_data.get('nin_loc', '')

            # Look up dummy data by NIN
            use_mock = getattr(settings, 'NID_MOCK_ENABLED', True)
            client = NIDClient(use_mock=use_mock)

            try:
                raw_data = client.fetch_by_nin(nin)
                # mapped_data = map_nid_to_spdci(raw_data)  # SPDCI mapping commented out
                return Response(raw_data, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": f"Internal Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NIDMediatorView(APIView):
    """
    Mediator endpoint that fetches data from an external NID API and returns it.
    """
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        parameters=[NIDFetchRequestSerializer],
        responses={200: NIDMappingResponseSerializer},
        description="Fetches raw NID data from external service by NIN."
    )
    def get(self, request):
        serializer = NIDFetchRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        nin = serializer.validated_data['nin']

        # Use mock client if enabled in settings or as a fallback
        use_mock = getattr(settings, 'NID_MOCK_ENABLED', True)
        client = NIDClient(use_mock=use_mock)

        try:
            # 1. Fetch raw data from external API (or dummy data)
            raw_data = client.fetch_by_nin(nin)

            # 2. Return raw key-value data directly (SPDCI mapping commented out)
            # mapped_data = map_nid_to_spdci(raw_data)
            return Response(raw_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Internal Mediator Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
