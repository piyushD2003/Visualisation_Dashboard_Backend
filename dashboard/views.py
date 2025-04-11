from rest_framework import viewsets, status
from rest_framework.response import Response
from datetime import datetime
from .models import Data
from .serializers import DataSerializer
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Min, Max

from rest_framework.parsers import MultiPartParser, FormParser
import json

class DataAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Support file uploads

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('datafile')  # Get file from request

        if not uploaded_file:
            return Response({"error": "No file uploaded. Expected key: 'datafile'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read and decode file content
            file_content = uploaded_file.read().decode('utf-8')
            payload = json.loads(file_content)  # Convert JSON string to Python list/dict
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format in uploaded file."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(payload, list):
            return Response({"error": "Expected a list of records in JSON file."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert date fields
        for record in payload:
            for key, value in record.items():
                if value == "":
                    record[key] = None

            date_fields = ['added', 'published']
            for field in date_fields:
                if field in record and record[field]:
                    try:
                        record[field] = datetime.strptime(record[field], "%B, %d %Y %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        return Response({field: "Invalid date format. Expected: 'Month, DD YYYY HH:MM:SS'"},
                                        status=status.HTTP_400_BAD_REQUEST)

        serializer = DataSerializer(data=payload, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DashboardView(APIView):
    def get(self, request):
        self.data = request.query_params
        self.pk = None

        # if not request.user.is_authenticated:
        #     return Response({"message": "Authentication credentials were not provided."},
        #                     status=status.HTTP_401_UNAUTHORIZED)

        if "id" in self.data:
            self.pk = self.data.get("id")

        if "action" in self.data:
            action = str(self.data["action"])
            action_mapper = {
                "getIntensity": self.getIntensity,
                "getFilter": self.getFilter,
                "getOverview":self.getOverview,
                "getTopicDistribution": self.getTopicDistribution,
                "getTrendsOverYears": self.getTrendsOverYears,
                "getWorldMapData": self.getWorldMapData,
                "getBubbleChartData": self.getBubbleChartData, 
            }
            action_status = action_mapper.get(action)
            if action_status:
                action_status(request)
            else:
                return Response({"message": "Choose Wrong Option !", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa
            return Response(self.ctx, self.status)
        else:
            return Response({"message": "Action is not in dict", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa
    
    def getFilter(self, request):
        """
        Fetches unique values for dropdown filters in the dashboard.
        """
        try:
            self.ctx = {
                # Time-Based Filters
                "start_years": list(Data.objects.exclude(start_year="").values_list("start_year", flat=True).distinct()),
                "end_years": list(Data.objects.exclude(end_year="").values_list("end_year", flat=True).distinct()),

                "intensity_range": {
                    "min": Data.objects.aggregate(min_intensity=Min("intensity"))["min_intensity"],
                    "max": Data.objects.aggregate(max_intensity=Max("intensity"))["max_intensity"],
                },
                "likelihood_range": {
                    "min": Data.objects.aggregate(min_likelihood=Min("likelihood"))["min_likelihood"],
                    "max": Data.objects.aggregate(max_likelihood=Max("likelihood"))["max_likelihood"],
                },
                "relevance_range": {
                    "min": Data.objects.aggregate(min_relevance=Min("relevance"))["min_relevance"],
                    "max": Data.objects.aggregate(max_relevance=Max("relevance"))["max_relevance"],
                },
                "impact_range": {
                    "min": Data.objects.aggregate(min_impact=Min("impact"))["min_impact"],
                    "max": Data.objects.aggregate(max_impact=Max("impact"))["max_impact"],
                },

                "end_year": list(Data.objects.exclude(end_year="").values_list("end_year", flat=True).distinct()),
                "topic": list(Data.objects.exclude(topic="").values_list("topic", flat=True).distinct()),
                "region": list(Data.objects.exclude(region="").values_list("region", flat=True).distinct()),
                "country": list(Data.objects.exclude(country="").values_list("country", flat=True).distinct()),
                # "cities": list(Data.objects.exclude(city="").values_list("city", flat=True).distinct()),
                "sector": list(Data.objects.exclude(sector="").values_list("sector", flat=True).distinct()),
                "pestle": list(Data.objects.exclude(pestle="").values_list("pestle", flat=True).distinct()),
                "source": list(Data.objects.exclude(source="").values_list("source", flat=True).distinct()),

                # SWOT Categories
                "swot": ["Strength", "Weakness", "Opportunity", "Threat"],
            }
            self.status = status.HTTP_200_OK

        except Exception as e:
            self.ctx = {"message": f"Error fetching filters: {str(e)}"}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def getOverview(self, request):
        try:
            self.ctx = {
            # Averages
            "avg_intensity": Data.objects.aggregate(avg_intensity=Avg("intensity"))["avg_intensity"],
            "avg_likelihood": Data.objects.aggregate(avg_likelihood=Avg("likelihood"))["avg_likelihood"],
            "avg_relevance": Data.objects.aggregate(avg_relevance=Avg("relevance"))["avg_relevance"],

            # Distributions
            "end_year_distribution": Data.objects.values("end_year").annotate(count=Count("end_year")),
            "country_distribution": Data.objects.values("country").annotate(count=Count("country")),
            "topic_distribution": Data.objects.values("topic").annotate(count=Count("topic")),
            "region_distribution": Data.objects.values("region").annotate(count=Count("region")),

            # Totals
            "total_topic": Data.objects.exclude(topic="").values("topic").distinct().count(),
            "total_country": Data.objects.exclude(country="").values("country").distinct().count(),
            "total_region": Data.objects.exclude(region="").values("region").distinct().count(),
        }
            self.status = status.HTTP_200_OK

        except Exception as e:
            self.ctx = {"message": f"Error fetching filters: {str(e)}"}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def getIntensity(self, request):
        """
        Fetches intensity data for visualization (bar chart or heatmap).
        Filters based on query parameters.
        """
        try:
            # Fetch data, apply filters
            queryset = Data.objects.all()

            # Optional Filters
            end_year = request.query_params.get("end_year")
            country = request.query_params.get("country")
            topic = request.query_params.get("topic")
            region = request.query_params.get("region")

            if end_year:
                queryset = queryset.filter(end_year=end_year)
            if country:
                queryset = queryset.filter(country__icontains=country)
            if topic:
                queryset = queryset.filter(topic__icontains=topic)
            if region:
                queryset = queryset.filter(region__icontains=region)

            # Aggregate Data for Visualization
            intensity_data = queryset.values("country").annotate(avg_intensity=Avg("intensity")).order_by("-avg_intensity")

            # Pagination
            page_number = int(request.query_params.get("page", 1))
            records_number = int(request.query_params.get("records_number", 10))

            paginator = Paginator(intensity_data, records_number)
            page_data = paginator.page(page_number)

            # Response
            self.ctx = {
                "message": "Successfully fetched intensity data!",
                "data": list(page_data),
                "total_count": queryset.count(),
            }
            self.status = status.HTTP_200_OK

        except Exception as e:
            self.ctx = {"message": f"Error fetching intensity data: {str(e)}"}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def getTopicDistribution(self, request):
        """
        Fetches topic distribution data for visualization (Pie Chart / Treemap).
        Supports filtering by sector, region, country, PEST, and SWOT.
        """
        try:
            queryset = Data.objects.all()

            # Apply filters
            sector = request.query_params.get("sector")
            region = request.query_params.get("region")
            country = request.query_params.get("country")
            pestle = request.query_params.get("pestle")
            swot = request.query_params.get("swot")

            if sector:
                queryset = queryset.filter(sector__icontains=sector)
            if region:
                queryset = queryset.filter(region__icontains=region)
            if country:
                queryset = queryset.filter(country__icontains=country)
            if pestle:
                queryset = queryset.filter(pestle__icontains=pestle)
            if swot:
                swot_mapping = {
                    "strength": "Economic",
                    "weakness": "Social",
                    "opportunity": "Technological",
                    "threat": "Political",
                }
                mapped_pestle = swot_mapping.get(swot.lower())
                if mapped_pestle:
                    queryset = queryset.filter(pestle__icontains=mapped_pestle)

            # Aggregate topic counts
            topic_distribution = queryset.values("topic").annotate(count=Count("topic")).order_by("-count")

            self.ctx = {
                "message": "Successfully fetched topic distribution data!",
                "data": list(topic_distribution),
                "total_topics": queryset.values("topic").distinct().count(),
            }
            self.status = status.HTTP_200_OK

        except Exception as e:
            self.ctx = {"message": f"Error fetching topic distribution data: {str(e)}"}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def getTrendsOverYears(self, request):
        """
        Fetches intensity, likelihood, and relevance trends over years for a Line Chart.
        Uses 'end_year' as X-axis (converted to integer for proper sorting).
        """
        try:
            queryset = Data.objects.exclude(end_year__isnull=True).exclude(end_year="")

            # Optional Filters
            country = request.query_params.get("country")
            region = request.query_params.get("region")
            sector = request.query_params.get("sector")
            topic = request.query_params.get("topic")

            if country:
                queryset = queryset.filter(country__icontains=country)
            if region:
                queryset = queryset.filter(region__icontains=region)
            if sector:
                queryset = queryset.filter(sector__icontains=sector)
            if topic:
                queryset = queryset.filter(topic__icontains=topic)

            # Convert end_year to integer and aggregate values
            # Convert end_year to integer manually and aggregate
            trends_data = (
                queryset
                .values("end_year")  # Keep it as a string first
                .annotate(
                    avg_intensity=Avg("intensity"),
                    avg_likelihood=Avg("likelihood"),
                    avg_relevance=Avg("relevance")
                )
                .order_by("end_year")  # Ensure ordering is correct
            )

            # Convert year to integer for proper visualization
            trends_data = [
                {
                    "year": int(entry["end_year"]),  # Convert string to integer safely
                    "avg_intensity": entry["avg_intensity"],
                    "avg_likelihood": entry["avg_likelihood"],
                    "avg_relevance": entry["avg_relevance"]
                }
                for entry in trends_data
            ]

            self.ctx = {
                "message": "Successfully fetched trends over years!",
                "data": trends_data,
            }
            self.status = status.HTTP_200_OK

        except Exception as e:
            self.ctx = {"message": f"Error fetching trends data: {str(e)}"}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def getWorldMapData(self, request):
        """
        Fetches country-level data for geographic distribution.
        Provides:
        - Total Events per Country (Distribution)
        - Average Intensity & Likelihood
        - Most Common Sector & Topic
        - PESTLE Analysis
        - SWOT Categorization (Derived from PESTLE)
        """
        try:
            queryset = Data.objects.exclude(country__isnull=True).exclude(country="")

            # Apply Filters
            region = request.query_params.get("region")
            country = request.query_params.get("country")
            sector = request.query_params.get("sector")
            topic = request.query_params.get("topic")
            pestle = request.query_params.get("pestle")
            swot = request.query_params.get("swot")

            intensity_min = request.query_params.get("intensity_min")
            intensity_max = request.query_params.get("intensity_max")
            likelihood_min = request.query_params.get("likelihood_min")
            likelihood_max = request.query_params.get("likelihood_max")

            if region:
                queryset = queryset.filter(region__icontains=region)
            if country:
                queryset = queryset.filter(country__icontains=country)
            if sector:
                queryset = queryset.filter(sector__icontains=sector)
            if topic:
                queryset = queryset.filter(topic__icontains=topic)
            if pestle:
                queryset = queryset.filter(pestle__icontains=pestle)
            if swot:
                swot_mapping = {
                    "strength": "Economic",
                    "weakness": "Social",
                    "opportunity": "Technological",
                    "threat": "Political",
                }
                mapped_pestle = swot_mapping.get(swot.lower())
                if mapped_pestle:
                    queryset = queryset.filter(pestle__icontains=mapped_pestle)

            # Handle min/max filters for intensity
            if intensity_min and intensity_max:
                queryset = queryset.filter(intensity__gte=intensity_min, intensity__lte=intensity_max)
            elif intensity_min:
                queryset = queryset.filter(intensity__gte=intensity_min)
            elif intensity_max:
                queryset = queryset.filter(intensity__lte=intensity_max)

            # Handle min/max filters for likelihood
            if likelihood_min and likelihood_max:
                queryset = queryset.filter(likelihood__gte=likelihood_min, likelihood__lte=likelihood_max)
            elif likelihood_min:
                queryset = queryset.filter(likelihood__gte=likelihood_min)
            elif likelihood_max:
                queryset = queryset.filter(likelihood__lte=likelihood_max)

            # Aggregate Country Data
            country_data = (
                queryset.values("country")
                .annotate(
                    total_events=Count("country"),
                    avg_intensity=Avg("intensity"),
                    avg_likelihood=Avg("likelihood"),
                    most_common_sector=Count("sector"),
                    most_common_topic=Count("topic"),
                    pestle_distribution=Count("pestle"),
                )
                .order_by("-total_events")  # Sort by event count
            )

            # Prepare Response
            self.ctx = {
                "message": "Successfully fetched world map data!",
                "data": list(country_data),
            }
            self.status = status.HTTP_200_OK

        except Exception as e:
            self.ctx = {"message": f"Error fetching world map data: {str(e)}"}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def getBubbleChartData(self, request):
        """
        Fetches data for a bubble chart comparing Relevance vs. Intensity.
        - X-Axis: Intensity
        - Y-Axis: Relevance
        - Bubble Size: Likelihood
        """
        try:
            queryset = Data.objects.exclude(intensity__isnull=True).exclude(relevance__isnull=True)

            # Apply Filters
            topic = request.query_params.get("topic")
            sector = request.query_params.get("sector")
            region = request.query_params.get("region")
            relevance_min = request.query_params.get("relevance_min")
            relevance_max = request.query_params.get("relevance_max")
            intensity_min = request.query_params.get("intensity_min")
            intensity_max = request.query_params.get("intensity_max")

            if topic:
                queryset = queryset.filter(topic__icontains=topic)
            if sector:
                queryset = queryset.filter(sector__icontains=sector)
            if region:
                queryset = queryset.filter(region__icontains=region)

            # Handle min/max filters for relevance
            if relevance_min and relevance_max:
                queryset = queryset.filter(relevance__gte=relevance_min, relevance__lte=relevance_max)
            elif relevance_min:
                queryset = queryset.filter(relevance__gte=relevance_min)
            elif relevance_max:
                queryset = queryset.filter(relevance__lte=relevance_max)

            # Handle min/max filters for intensity
            if intensity_min and intensity_max:
                queryset = queryset.filter(intensity__gte=intensity_min, intensity__lte=intensity_max)
            elif intensity_min:
                queryset = queryset.filter(intensity__gte=intensity_min)
            elif intensity_max:
                queryset = queryset.filter(intensity__lte=intensity_max)

            # Aggregate Data
            bubble_data = (
                queryset.values("topic", "sector", "country")
                .annotate(
                    avg_intensity=Avg("intensity"),
                    avg_relevance=Avg("relevance"),
                    avg_likelihood=Avg("likelihood"),
                    event_count=Count("id")  # Bubble Size → Represents number of events
                )
                .order_by("-event_count")  # Sort by event count
            )

            # Prepare Response
            self.ctx = {
                "message": "Successfully fetched bubble chart data!",
                "data": list(bubble_data),
            }
            self.status = status.HTTP_200_OK

        except Exception as e:
            self.ctx = {"message": f"Error fetching bubble chart data: {str(e)}"}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR

    