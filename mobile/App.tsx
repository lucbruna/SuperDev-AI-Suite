import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { PaperProvider } from 'react-native-paper';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import ScannerScreen from './src/screens/ScannerScreen';
import AIAssistantScreen from './src/screens/AIAssistantScreen';
import { AuthProvider } from './src/contexts/AuthContext';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <PaperProvider>
      <AuthProvider>
        <NavigationContainer>
          <Stack.Navigator initialRouteName="Login" screenOptions={{ headerStyle: { backgroundColor: '#3F51B5' }, headerTintColor: '#fff' }}>
            <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
            <Stack.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'SuperDev AI Suite' }} />
            <Stack.Screen name="Scanner" component={ScannerScreen} options={{ title: 'Security Scanner' }} />
            <Stack.Screen name="AIAssistant" component={AIAssistantScreen} options={{ title: 'AI Assistant' }} />
          </Stack.Navigator>
        </NavigationContainer>
        <StatusBar style="light" />
      </AuthProvider>
    </PaperProvider>
  );
}
