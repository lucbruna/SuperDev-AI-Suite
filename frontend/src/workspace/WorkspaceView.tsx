export function WorkspaceView() {
  return (
    <div className="flex h-full">
      <div className="w-64 bg-gray-900 text-white p-4">
        <h2 className="text-lg font-semibold mb-4">Files</h2>
        <div className="space-y-2 text-sm">
          <div className="hover:bg-gray-700 p-1 rounded cursor-pointer">src/</div>
          <div className="hover:bg-gray-700 p-1 rounded cursor-pointer">tests/</div>
          <div className="hover:bg-gray-700 p-1 rounded cursor-pointer">docs/</div>
          <div className="hover:bg-gray-700 p-1 rounded cursor-pointer">README.md</div>
        </div>
      </div>
      <div className="flex-1 bg-white p-4">
        <p className="text-gray-500">Select a file to view its contents</p>
      </div>
    </div>
  );
}
