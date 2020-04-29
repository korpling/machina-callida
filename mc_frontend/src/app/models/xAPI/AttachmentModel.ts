interface AttachmentModel {
  stream: ReadableStream; // NodeJS.ReadableStream
  hash: string;
  contentLength?: number;
  contentType: string;
}

export default AttachmentModel;
