from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from users.filters import UserFilter
from users.models import User
from users.serializers import (
    LoginSerializer,
    UserSerializer
)
from django.core.paginator import Paginator

class RegisterView(APIView):
    def post(self, request):
        # Extracting each field manually from the request data
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        # Validation for mandatory fields
        if not first_name or not last_name or not email or not phone or not password:
            return Response({'error': 'Please provide all required fields.'},  status=status.HTTP_400_BAD_REQUEST)

        # Checking if passwords match
        if password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        # Checking if email or phone already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(phone=phone).exists():
            return Response({'error': 'Phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Creating user object and saving manually
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone
        )

        # Hashing password and saving user
        user.set_password(password)
        user.save()

        # Generating JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Serializing the user data for response
        user_data = UserSerializer(user).data

        # Adding tokens to the response
        user_data['access'] = access_token
        user_data['refresh'] = refresh_token
        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            tokens = serializer.save()
            return Response(tokens, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserAPI(APIView):
    """MedicineData view"""
    # permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        self.data = request.GET
        self.pk = None
        if not request.user.is_authenticated:
            return Response({"message": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        if "id" in self.data:
            self.pk = self.data.get("id")

        if "action" in self.data:
            action = str(self.data["action"])
            action_mapper = {
                "getUser": self.getUser,
            }
            action_status = action_mapper.get(action)
            if action_status:
                action_status(request)
            else:
                return Response({"message": "Choose Wrong Option !", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa
            return Response(self.ctx, self.status)
        else:
            return Response({"message": "Action is not in dict", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa

    def getUser(self, request):
        filterset_class = UserFilter
        try:
            # get the page details
            page_number = int(self.data.get("page", 1))
            records_number = int(self.data.get("records_number", 10))

            data = User.objects.all()
            filtered_queryset = filterset_class(request.query_params, queryset=data).qs
            # calculating total records
            total_count = filtered_queryset.count()
            # Applying pagination
            paginator = Paginator(filtered_queryset, records_number)
            page_data = paginator.page(page_number)
            serializer = UserSerializer(page_data, many=True).data
            if self.pk and len(serializer):
                serializer = serializer[0]
            self.ctx = {"message": "successfully getting User!", "data": serializer, "total_count": total_count} # noqa
            self.status = status.HTTP_200_OK
        except Exception:
            self.ctx = {"message": "not getting data!"}
            self.status = status.HTTP_404_NOT_FOUND

    def post(self, request):
        self.data = request.data
        self.pk = None
        self.user = request.user
        if not request.user.is_authenticated:
            return Response({"message": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        if "id" in self.data:
            self.pk = self.data.get("id")

        if "action" in self.data:
            action = str(self.data["action"])
            action_mapper = {
                "postUser": self.postUser,
                # Add more actions as needed
            }

            action_status = action_mapper.get(action)
            if action_status:
                action_status()
            else:
                return Response({"message": "Choose Wrong Option !", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa
            return Response(self.ctx, self.status)
        else:
            return Response({"message": "Action is not in dict", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa

    def postUser(self):
        first_name = self.data.get("first_name")
        last_name = self.data.get("last_name")
        email = self.data.get("email")
        phone = self.data.get("phone")

        try:
            obj = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )
            obj.save()
            serializer = UserSerializer(obj).data
            self.ctx = {"message": "User is Created!", "data": serializer} # noqa
            self.status = status.HTTP_201_CREATED
        except Exception as e:
            self.ctx = {"message": "Something went wrong!", "error_msg": str(e)}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def patch(self, request):
        self.data = request.data
        self.pk = None
        self.user = request.user
        if not request.user.is_authenticated:
            return Response({"message": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        if "id" in self.data:
            self.id = self.data["id"]

        if "action" in self.data:
            action = str(self.data["action"])
            action_mapper = {
                "patchUser": self.patchUser,
                "patchDoctorPersonalDetail": self.patchDoctorPersonalDetail

            }
            action_status = action_mapper.get(action)
            if action_status:
                action_status()
            else:
                return Response({"message": "Choose Wrong Option !", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa
            return Response(self.ctx, self.status)
        else:
            return Response({"message": "Action is not in dict", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa

    def patchUser(self):
        first_name = self.data.get("first_name")
        last_name = self.data.get("last_name")
        email = self.data.get("email")
        phone = self.data.get("phone")

        try:
            users = User.objects.filter(pk=self.id)
            if users.exists():
                users = users[0]
            else:
                self.ctx = {"message": f"users id {self.id} Not Found!"}
                self.status = status.HTTP_404_NOT_FOUND
                return
            if first_name:
                users.first_name = first_name
            if last_name:
                users.last_name = last_name
            if phone:
                users.phone = phone
            if email:
                users.email = email
            users.save()
            serializer = UserSerializer(users).data
            self.ctx = {"message": "users is Updated!", "data": serializer}
            self.status = status.HTTP_201_CREATED
        except Exception as e:
            self.ctx = {"message": "Something went wrong!", "error_msg": str(e)}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def delete(self, request):
        self.data = request.data
        self.pk = None
        if not request.user.is_authenticated:
            return Response({"message": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        if "id" in self.data:
            self.id = self.data["id"]

        if "action" in self.data:
            action = str(self.data["action"])
            action_mapper = {
                "delUser": self.delUser,
            }
            action_status = action_mapper.get(action)
            if action_status:
                action_status()
            else:
                return Response({"message": "Choose Wrong Option !", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa
            return Response(self.ctx, self.status)
        else:
            return Response({"message": "Action is not in dict", "data": None}, status.HTTP_400_BAD_REQUEST) # noqa

    def delUser(self):
        try:
            data = User.objects.get(pk=self.id)
            if data:
                data.delete()
            self.ctx = {"message": "User deleted!"}
            self.status = status.HTTP_201_CREATED
        except User.DoesNotExist:
            self.ctx = {"message": "User id Not Found!"}
            self.status = status.HTTP_404_NOT_FOUND
        except Exception as e:
            self.ctx = {"message": "Something went wrong!", "error_msg": str(e)}
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR

