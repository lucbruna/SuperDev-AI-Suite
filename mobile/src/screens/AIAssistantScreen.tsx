import React, { useState, useRef } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Text, TextInput, Button, SegmentedButtons } from 'react-native-paper';
import { aiAPI } from '../api/client';

export default function AIAssistantScreen() {
  const [mode, setMode] = useState('reason');
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      let res;
      switch (mode) {
        case 'reason':
          res = await aiAPI.reason({ prompt: input });
          setResponse(res.data?.result || JSON.stringify(res.data));
          break;
        case 'plan':
          res = await aiAPI.plan({ goal: input });
          setResponse(JSON.stringify(res.data, null, 2));
          break;
        case 'code':
          res = await aiAPI.generateCode({ description: input, language: 'python' });
          setResponse(res.data?.code || JSON.stringify(res.data));
          break;
        case 'security':
          res = await aiAPI.analyzeSecurity({ code: input, language: 'python' });
          setResponse(JSON.stringify(res.data, null, 2));
          break;
      }
    } catch (e: any) {
      setResponse(`Error: ${e.response?.data?.detail || e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <SegmentedButtons
            value={mode}
            onValueChange={setMode}
            buttons={[
              { value: 'reason', label: 'Reason' },
              { value: 'plan', label: 'Plan' },
              { value: 'code', label: 'Code' },
              { value: 'security', label: 'Security' },
            ]}
            style={styles.segmented}
          />
          <TextInput
            label={mode === 'code' ? 'Describe what to generate' : mode === 'security' ? 'Paste code to analyze' : 'Enter your prompt'}
            value={input}
            onChangeText={setInput}
            mode="outlined"
            multiline
            numberOfLines={4}
            style={styles.input}
          />
          <Button mode="contained" onPress={send} loading={loading} icon="send">Send</Button>
        </Card.Content>
      </Card>

      {response ? (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium">Response</Text>
            <ScrollView style={styles.responseScroll}>
              <Text style={styles.responseText}>{response}</Text>
            </ScrollView>
          </Card.Content>
        </Card>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5', padding: 16 },
  card: { marginBottom: 16 },
  segmented: { marginBottom: 12 },
  input: { marginBottom: 12 },
  responseScroll: { maxHeight: 300, marginTop: 8 },
  responseText: { fontFamily: 'monospace', fontSize: 13 },
});
