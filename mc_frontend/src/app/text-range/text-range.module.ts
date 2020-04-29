import {RouterModule, Routes} from '@angular/router';
import {IonicModule} from '@ionic/angular';
import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {TranslateModule} from '@ngx-translate/core';
import {FormsModule} from '@angular/forms';
import {TextRangePage} from 'src/app/text-range/text-range.page';

const routes: Routes = [
  {
    path: '',
    component: TextRangePage
  }
];

@NgModule({
  declarations: [
    TextRangePage,
  ],
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    RouterModule.forChild(routes),
    TranslateModule.forChild()
  ],
})
export class TextRangePageModule {
}
