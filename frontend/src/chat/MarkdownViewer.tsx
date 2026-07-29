import React from 'react';
import Image from 'next/image';
import CodePreview from './CodePreview';

interface MarkdownViewerProps {
  content: string;
}

export default function MarkdownViewer({ content }: MarkdownViewerProps) {
  const segments = parseMarkdown(content);

  return (
    <div className="markdown-content space-y-2 text-sm leading-relaxed">
      {segments.map((segment, i) => {
        switch (segment.type) {
          case 'code':
            return (
              <CodePreview
                key={i}
                code={segment.content}
                language={segment.language}
              />
            );
          case 'heading':
            return (
              <h2 key={i} className="text-base font-semibold text-gray-100">
                {renderInline(segment.content)}
              </h2>
            );
          case 'heading2':
            return (
              <h3 key={i} className="text-sm font-semibold text-gray-200">
                {renderInline(segment.content)}
              </h3>
            );
          case 'list':
            return (
              <ul key={i} className="list-disc pl-5 space-y-0.5">
                {segment.items?.map((item, j) => (
                  <li key={j} className="text-gray-300">{renderInline(item)}</li>
                ))}
              </ul>
            );
          case 'ordered-list':
            return (
              <ol key={i} className="list-decimal pl-5 space-y-0.5">
                {segment.items?.map((item, j) => (
                  <li key={j} className="text-gray-300">{renderInline(item)}</li>
                ))}
              </ol>
            );
          case 'table':
            return (
              <div key={i} className="overflow-x-auto">
                <table className="min-w-full border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-gray-700">
                      {segment.headers?.map((h, j) => (
                        <th key={j} className="px-3 py-1.5 text-left font-medium text-gray-300">
                          {renderInline(h)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {segment.rows?.map((row, j) => (
                      <tr key={j} className="border-b border-gray-800">
                        {row.map((cell, k) => (
                          <td key={k} className="px-3 py-1 text-gray-400">
                            {renderInline(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          case 'blockquote':
            return (
              <blockquote key={i} className="border-l-2 border-gray-600 pl-3 italic text-gray-400">
                {renderInline(segment.content)}
              </blockquote>
            );
          case 'hr':
            return <hr key={i} className="my-2 border-gray-800" />;
          case 'paragraph':
          default:
            return (
              <p key={i} className="text-gray-200">
                {renderInline(segment.content)}
              </p>
            );
        }
      })}
    </div>
  );
}

function renderInline(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    const boldMatch = remaining.match(/^(\*\*|__)(.+?)\1/);
    if (boldMatch) {
      parts.push(<strong key={key++} className="font-semibold text-gray-100">{renderInline(boldMatch[2])}</strong>);
      remaining = remaining.slice(boldMatch[0].length);
      continue;
    }

    const italicMatch = remaining.match(/^(\*|_)(.+?)\1/);
    if (italicMatch) {
      parts.push(<em key={key++} className="italic text-gray-300">{renderInline(italicMatch[2])}</em>);
      remaining = remaining.slice(italicMatch[0].length);
      continue;
    }

    const codeMatch = remaining.match(/^`(.+?)`/);
    if (codeMatch) {
      parts.push(
        <code key={key++} className="rounded bg-gray-800 px-1 py-0.5 text-[11px] font-mono text-orange-300">
          {codeMatch[1]}
        </code>
      );
      remaining = remaining.slice(codeMatch[0].length);
      continue;
    }

    const linkMatch = remaining.match(/^\[(.+?)\]\((.+?)\)/);
    if (linkMatch) {
      parts.push(
        <a key={key++} href={linkMatch[2]} target="_blank" rel="noopener noreferrer"
           className="text-blue-400 underline hover:text-blue-300">
          {linkMatch[1]}
        </a>
      );
      remaining = remaining.slice(linkMatch[0].length);
      continue;
    }

    const imageMatch = remaining.match(/^!\[(.+?)\]\((.+?)\)/);
    if (imageMatch) {
      parts.push(
        <Image key={key++} src={imageMatch[2]} alt={imageMatch[1]} width={800} height={600} className="max-w-full rounded-lg my-1" loading="lazy" />
      );
      remaining = remaining.slice(imageMatch[0].length);
      continue;
    }

    const nlMatch = remaining.match(/^\\n/);
    if (nlMatch) {
      parts.push(<br key={key++} />);
      remaining = remaining.slice(nlMatch[0].length);
      continue;
    }

    parts.push(remaining[0]);
    remaining = remaining.slice(1);
  }

  return parts;
}

interface Segment {
  type: string;
  content: string;
  language?: string;
  items?: string[];
  headers?: string[];
  rows?: string[][];
}

function parseMarkdown(md: string): Segment[] {
  const lines = md.split('\n');
  const segments: Segment[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith('```')) {
      const lang = line.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      segments.push({ type: 'code', content: codeLines.join('\n'), language: lang || undefined });
      i++;
      continue;
    }

    if (line.startsWith('#')) {
      const level = line.match(/^#+/)![0].length;
      const content = line.replace(/^#+\s*/, '');
      if (level <= 2) {
        segments.push({ type: 'heading', content });
      } else {
        segments.push({ type: 'heading2', content });
      }
      i++;
      continue;
    }

    if (line.startsWith('---') || line.startsWith('***') || line.startsWith('___')) {
      segments.push({ type: 'hr', content: '' });
      i++;
      continue;
    }

    if (line.startsWith('> ')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].startsWith('> ')) {
        quoteLines.push(lines[i].slice(2));
        i++;
      }
      segments.push({ type: 'blockquote', content: quoteLines.join('\n') });
      continue;
    }

    if (line.startsWith('- ') || line.startsWith('* ')) {
      const items: string[] = [];
      while (i < lines.length && (lines[i].startsWith('- ') || lines[i].startsWith('* '))) {
        items.push(lines[i].slice(2));
        i++;
      }
      segments.push({ type: 'list', content: '', items });
      continue;
    }

    if (/^\d+\.\s/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s*/, ''));
        i++;
      }
      segments.push({ type: 'ordered-list', content: '', items });
      continue;
    }

    if (line.includes('|') && lines[i + 1]?.includes('---')) {
      const headers = line.split('|').map((h) => h.trim()).filter(Boolean);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && lines[i].includes('|')) {
        const row = lines[i].split('|').map((c) => c.trim()).filter(Boolean);
        if (row.length > 0) rows.push(row);
        i++;
      }
      segments.push({ type: 'table', content: '', headers, rows });
      continue;
    }

    if (line.trim() === '') {
      i++;
      continue;
    }

    const paraLines: string[] = [];
    while (i < lines.length && lines[i].trim() !== '' && !lines[i].startsWith('#')) {
      paraLines.push(lines[i]);
      i++;
    }
    segments.push({ type: 'paragraph', content: paraLines.join('\n') });
  }

  return segments;
}
