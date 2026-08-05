# SuperDev AI Suite Mobile v5.0

Enterprise-grade Flutter mobile application for the SuperDev AI Suite platform.

## Features

- **Dashboard** - Real-time business metrics and quick actions
- **Enterprise Suite** - Full ERP, CRM, PDV, Inventory, and Finance modules
- **AI Assistant** - Intelligent chat interface with code highlighting
- **QR/Barcode Scanner** - Scan products, generate QR codes, scan history
- **Profile & Settings** - User management, theme toggle, API configuration

## Prerequisites

- Flutter SDK >= 3.0.0
- Dart SDK >= 3.0.0
- Android Studio / Xcode for platform builds
- A running instance of the SuperDev AI Suite backend API

## Setup

1. **Clone and install dependencies**
```bash
cd mobile
flutter pub get
```

2. **Configure API URL**
   - Default: `http://localhost:8000/api`
   - Change via environment variable or in-app Settings

3. **Run the app**
```bash
flutter run
```

4. **Build for production**
```bash
flutter build apk --release
flutter build ios --release
```

## Project Structure

```
mobile/
├── lib/
│   ├── config/          - API config, theme
│   ├── models/          - Data models (User, Product, Lead, etc.)
│   ├── services/        - API client, Auth, Enterprise, Scanner services
│   ├── providers/       - State management (Auth, Enterprise)
│   ├── screens/         - UI screens
│   │   └── enterprise/  - ERP, CRM, PDV, Inventory, Finance
│   ├── widgets/         - Reusable components (charts, badges, loaders)
│   └── main.dart        - App entry point
├── android/             - Android platform config
├── ios/                 - iOS platform config
└── pubspec.yaml         - Dependencies
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `http://localhost:8000/api` |

## Dependencies

- `provider` - State management
- `http` - HTTP client
- `flutter_secure_storage` - Secure token storage
- `shared_preferences` - Local preferences
- `fl_chart` - Charts and graphs
- `mobile_scanner` - QR/Barcode scanning
- `qr_flutter` - QR code generation
- `flutter_local_notifications` - Push notifications
- `url_launcher` - External URL handling

## Architecture

- **State Management**: Provider pattern with ChangeNotifier
- **API Layer**: Singleton ApiClient with token refresh and retry logic
- **Models**: Immutable data classes with JSON serialization
- **Services**: Business logic encapsulation
- **Screens**: Feature-based screen organization

## License

SuperDev AI Suite v5.0
