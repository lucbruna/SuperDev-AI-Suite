import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, Alert } from 'react-native';
import { Card, Text, TextInput, Button, SegmentedButtons, DataTable } from 'react-native-paper';
import { scannerAPI } from '../api/client';

const SCANNER_TYPES = [
  { value: 'source_code', label: 'Source Code' },
  { value: 'secrets', label: 'Secrets' },
  { value: 'dependencies', label: 'Dependencies' },
  { value: 'docker', label: 'Docker' },
  { value: 'kubernetes', label: 'Kubernetes' },
];

export default function ScannerScreen() {
  const [scannerType, setScannerType] = useState('source_code');
  const [target, setTarget] = useState('.');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const runScan = async () => {
    setLoading(true);
    try {
      const res = await scannerAPI.runScan({ scanner_type: scannerType, target });
      setResults(res.data);
    } catch (e: any) {
      Alert.alert('Scan Failed', e.response?.data?.detail || 'Error running scan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.sectionTitle}>Scanner Configuration</Text>
          <SegmentedButtons value={scannerType} onValueChange={setScannerType} buttons={SCANNER_TYPES} style={styles.segmented} />
          <TextInput label="Target Path" value={target} onChangeText={setTarget} mode="outlined" style={styles.input} />
          <Button mode="contained" onPress={runScan} loading={loading} icon="magnify">Run Scan</Button>
        </Card.Content>
      </Card>

      {results && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium">Results</Text>
            <DataTable>
              <DataTable.Header>
                <DataTable.Title>Severity</DataTable.Title>
                <DataTable.Title>Message</DataTable.Title>
              </DataTable.Header>
              {(results.findings || []).map((f: any, i: number) => (
                <DataTable.Row key={i}>
                  <DataTable.Cell>{f.severity}</DataTable.Cell>
                  <DataTable.Cell>{f.message}</DataTable.Cell>
                </DataTable.Row>
              ))}
            </DataTable>
          </Card.Content>
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5', padding: 16 },
  card: { marginBottom: 16 },
  sectionTitle: { marginBottom: 12, fontWeight: 'bold' },
  segmented: { marginBottom: 12 },
  input: { marginBottom: 12 },
});
