export * from './CreateEvent.tsx';
export * from './FetchEvents.tsx';
export * from './PersonalRoute.tsx';

export interface Event {
  id: number;
  name: string;
  date?: Date;
}

export const getName = (event: Event) => {
  return event.name;
};
