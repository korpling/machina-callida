import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { SemanticsPage } from './semantics.page';

const routes: Routes = [
  {
    path: '',
    component: SemanticsPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class SemanticsPageRoutingModule {}
